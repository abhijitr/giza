# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import datetime
from distutils import dir_util
import itertools
from jinja2 import Environment
import logging.config
import os
import sys
import re
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.renderers import JSON
from pyramid.security import unauthenticated_userid
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid_jinja2 import renderer_factory
import simplejson as json
from sqlalchemy import engine_from_config
from webassets import Bundle

from cleaver.base import Cleaver
from cleaver.backend.db import SQLAlchemyBackend

from .config import settings
from .models import initialize_sql
from . import logic
from .views.resources import (
    Root,
    GizaRequest
)
import urllib
from markupsafe import Markup

try:
    import uwsgi
    from uwsgidecorators import timer 
except ImportError:
    uwsgi = None
    timer = None

def configure_logging(config):
    logging.config.dictConfig(config.registry.settings['giza.logging'])


def configure_version(config):
    import subprocess

    # Get the latest commit hash from git
    proc = subprocess.Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
    out, err = proc.communicate()
    version = out[:7]
    config.registry.settings['giza.server_version'] = version


def configure_jinja(config):
    config.include('pyramid_jinja2')
    config.add_renderer('.html', renderer_factory)
    config.add_renderer('.tmpl', renderer_factory)

    json_renderer = JSON(serializer=json.dumps)
    def datetime_adapter(obj, request):
        return obj.isoformat()
    json_renderer.add_adapter(datetime.datetime, datetime_adapter)    
    config.add_renderer('json', json_renderer)

    the_settings = config.registry.settings

    def silent_none(value):
        if value is None:
            return ''
        return value

    jinja2_env = config.get_jinja2_environment()
    jinja2_env.finalize = silent_none

    # add custom template filters
    def to_json(value):
        return json.dumps(value)

    jinja2_env.filters['to_json'] = to_json
    
    def urlencode_filter(s):
        if type(s) == 'Markup':
            s = s.unescape()
        s = s.encode('utf8')
        s = urllib.quote_plus(s)
        return Markup(s)

    jinja2_env.filters['urlencode'] = urlencode_filter

    config.include('pyramid_webassets')
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    assets_env = config.get_webassets_env()
    assets_env.config['less_run_in_debug'] = False # set env variables before any bundles are created
    jinja2_env.assets_environment = assets_env

    deps_app = ['**/*.js','**/*.hbs']
    jsmin_app = Bundle(
        'app/js/build.js',
        filters=the_settings['giza.js_filters'],
        output='js/app-%(version)s.min.js',
        depends=deps_app if assets_env.debug else []
    )
    config.add_webasset('jsmin_app', jsmin_app)

    less_app = Bundle(
        'app/less/app.less',
        filters='less',
        output='css/app-%(version)s.css',
        extra={'rel': 'stylesheet/less' if assets_env.debug else 'stylesheet'}
    )
    config.add_webasset('less_app', less_app)

    # Clean up some loose ends for the asset pipeline
    base = os.path.dirname(__file__)

    if the_settings['giza.clear_asset_cache']:
        for d in ['/static/.webassets-cache', '/static/img', '/static/js', '/static/css']:
            if os.path.isdir(base + d):
                dir_util.remove_tree(base + d)
    
    # copy images to their final destination
    if os.path.isdir(base + '/static/vendor/img'):
        dir_util.copy_tree(base + '/static/vendor/img', base + '/static/img', update=True)
    if os.path.isdir(base + '/static/app/img'):
        dir_util.copy_tree(base + '/static/app/img', base + '/static/img', update=True)


def configure_auth(config):
    def get_current_user(request):
        # NOTE: we have to use unauthenticated_userid below. This just cracks open
        # the auth cookie and returns the id therein without further verification.
        # Specifically, we cannot use authenticated_userid because this will call
        # get_principals, defined below. This would cause infinite recursion.
        uid = unauthenticated_userid(request)
        user = logic.user.try_get(uid) if uid is not None else None
        return user

    def get_impersonator_user(request):
        uid = request.session.get('impersonator_id')
        user = logic.user.try_get(uid) if uid is not None else None
        return user

    def get_principals(user_id, request):
        """ Return the set of security principals for this request. None means
        unauthenticated, empty list means authenticated but has no principals
        associated.
        """
        user = request.current_user
        impersonator = request.impersonator_user

        if user:
            principals = [str(user.id)] # at minimum, user is his own principal
            principals.extend(user.groups or [])
            if impersonator:
                principals.extend(impersonator.groups or [])
            principals = list(set(principals))
        else:
            principals = None

        return principals

    the_settings = config.registry.settings

    policy = AuthTktAuthenticationPolicy(
        the_settings['giza.authn_secret'],
        hashalg='sha512',
        callback=get_principals,
        cookie_name=str(the_settings['giza.auth_cookie']) # can't be unicode
    )
    config.set_authentication_policy(policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())

    config.add_request_method(get_current_user, str('current_user'), reify=True)
    config.add_request_method(get_impersonator_user, str('impersonator_user'), reify=True)

    session_cookie_name = str(the_settings['giza.session_cookie']) # can't be unicode
    session_secret = str(the_settings['giza.session_secret'])
    factory = UnencryptedCookieSessionFactoryConfig(
        session_secret,
        timeout=86400*365,
        cookie_max_age=86400*365,
        cookie_name=session_cookie_name,
    )
    config.set_session_factory(factory)


def configure_helpers(config):
    def is_https(request):
        return request.environ.get('HTTP_X_FORWARDED_PROTO', '').lower() == 'https'

    def get_cleaver(request):
        """ For retrieving the A/B Testing toolkit
            
            Usage: 
            cleaver = request.get_cleaver()
            
            button_size = cleaver(
                'Button Size',
                ('Small', 12),
                ('Medium', 18),
                ('Large', 24)
            )
            where each () is (name of variant, value returned by cleaver)

            and then to mark a conversion: 
            
            cleaver.score('Button Size')
        """ 
        cleaver = Cleaver(
            environ=request.environ,
            identity=lambda environ: request.session.get('session_uid'),
            backend=SQLAlchemyBackend(request.registry.settings['giza.cleaver_backend']),
            count_humans_only=False
        )
        return cleaver

    config.add_request_method(is_https, str('is_https'), reify=True)
    config.add_request_method(get_cleaver)


def configure_redirects(config):
    config.include('pyramid_rewrite')
    
    config.add_rewrite_rule(r'/favicon.ico', r'/static/favicon.ico')
    config.add_rewrite_rule(r'/robots.txt', r'/static/robots.txt')
    config.add_rewrite_rule(r'/privacy-policy.pdf', r'/static/privacy-policy.pdf')

 
def configure_routes(config):
    cache_max_age = 86400 * 365
    config.add_static_view('static', 'static', cache_max_age=cache_max_age)
    config.add_static_view('css', 'static/css', cache_max_age=cache_max_age)
    config.add_static_view('img', 'static/img', cache_max_age=cache_max_age)
    config.add_static_view('js', 'static/js', cache_max_age=cache_max_age)

    config.add_route('home', '/')


def configure_db(config):
    from .utils import pgutil

    the_settings = config.registry.settings
    connect_args = {'connection_factory': pgutil.create_logging_connection}
    engine = engine_from_config(the_settings, 'sqlalchemy.', connect_args=connect_args)
    initialize_sql(engine)


# File change checking adapted from Werkzeug code
file_mtimes = {} # init static
def check_for_modifications(signum):
    global file_mtimes

    def iter_module_files():
        for module in sys.modules.values():
            filename = getattr(module, '__file__', None)
            if filename:
                old = None
                while not os.path.isfile(filename):
                    old = filename
                    filename = os.path.dirname(filename)
                    if filename == old:
                        break
                else:
                    if filename[-4:] in ('.pyc', '.pyo'):
                        filename = filename[:-1]
                    yield filename

    def iter_assets():
        base = os.path.dirname(os.path.dirname(__file__))
        for root, dirnames, filenames in os.walk(base + 'static'):
            for filename in filenames:
                if filename.endswith('.js') or filename.endswith('.less'):
                    yield os.path.join(root, filename)

    mtimes = file_mtimes
    for filename in itertools.chain(iter_module_files(), iter_assets()):
        try:
            mtime = os.stat(filename).st_mtime
        except OSError:
            continue

        old_time = mtimes.get(filename)
        if old_time is None:
            mtimes[filename] = mtime
            continue
        elif mtime > old_time:
            uwsgi.reload()
            return
            

def configure_file_watcher(config):
    if (uwsgi and timer and config.registry.settings['giza.enable_file_watcher']):
        the_timer = timer(3)
        the_timer(check_for_modifications)


def main(global_config, **local_config):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """

    the_settings = settings.load_settings(global_config, local_config)

    request_factory = None
    if os.environ.get('mock_request'):
        request_factory = GizaRequest
    config = Configurator(settings=the_settings, root_factory=Root, request_factory=request_factory)

    # NOTE: configure_jinja should come last because pyramid_webassets 
    # registers a static view with default settings. Since we register our own
    # static views with custom cache_max_age, we want those views to come first
    # (since the router goes in the order in which views are added).
    configure_logging(config)
    configure_version(config)
    configure_file_watcher(config)
    configure_db(config)
    configure_auth(config)
    configure_redirects(config)
    configure_routes(config)
    configure_jinja(config)
    configure_helpers(config)

    config.scan('.views')

    return config.make_wsgi_app()
