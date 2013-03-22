# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from distutils import dir_util
from jinja2 import Environment
import os
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import authenticated_userid
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid_jinja2 import renderer_factory
from sqlalchemy import engine_from_config
from webassets import Bundle

from .config import settings
from .models import initialize_sql
from .views.resources import Root

def silent_none(value):
    if value is None:
        return ''
    return value


def get_current_user(request):
    return None
    """
    uid = authenticated_userid(request)
    user = api.profile.get_user(user_id=uid) if uid is not None else None
    return user
    """


def get_impersonator_user(request):
    return None
    """
    uid = request.session.get('impersonator_id')
    user = api.profile.get_user(user_id=uid) if uid is not None else None
    return user
    """


def groupfinder(user_id, request):
    groups = None # unknown/unauthed user
    """
    try:
        groups = api.auth.get_groups(user_id)
    except api.ApiError:
        pass
    """

    return groups 


def configure_jinja(config):
    config.include('pyramid_jinja2')
    config.add_renderer('.html', renderer_factory)
    config.add_renderer('.tmpl', renderer_factory)

    jinja2_env = config.get_jinja2_environment()
    jinja2_env.finalize = silent_none

    config.include('pyramid_webassets')
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    assets_env = config.get_webassets_env()
    jinja2_env.assets_environment = assets_env
    assets_env.config['less_run_in_debug'] = False

    jsmin = Bundle(
        'vendor/js/bootstrap.js',
        'vendor/js/underscore.js',
        'vendor/js/backbone.js',
        'app/js/main.js',
        filters='uglifyjs',
        output='js/main-%(version)s.min.js'
    )
    config.add_webasset('jsmin', jsmin)

    less = Bundle(
        'vendor/less/bootstrap.less',
        'vendor/less/responsive.less',
        'app/less/app.less',
        filters='less',
        output='css/app-%(version)s.css',
        extra={'rel': 'stylesheet/less' if assets_env.debug else 'stylesheet'}
    )
    config.add_webasset('less', less)

    # copy images to their final destination
    base = os.path.dirname(__file__)
    dir_util.copy_tree(base+'/static/vendor/img', base+'/static/img', update=True)
    dir_util.copy_tree(base+'/static/app/img', base+'/static/img', update=True)


def configure_auth(config):
    the_settings = config.registry.settings

    auth_policy_secret = the_settings['giza.authn_secret']
    policy = AuthTktAuthenticationPolicy(
        auth_policy_secret,
        callback=groupfinder,
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


def configure_routes(config):
    cache_max_age = 86400 * 365 
    config.add_static_view('static', 'static', cache_max_age=cache_max_age)
    config.add_static_view('css', 'static/css', cache_max_age=cache_max_age)
    config.add_static_view('img', 'static/img', cache_max_age=cache_max_age)
    config.add_static_view('js', 'static/js', cache_max_age=cache_max_age)

    config.add_route('landing', '')
    config.add_route('track', 'track')
    config.add_route('admin-impersonate', 'admin/impersonate')


def configure_db(config):
    the_settings = config.registry.settings
    engine = engine_from_config(the_settings, 'sqlalchemy.')
    initialize_sql(engine)


def main(global_config, **local_config):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    the_settings = settings.load_settings(global_config, local_config)

    config = Configurator(settings=the_settings, root_factory=Root)

    # NOTE: configure_jinja should come last because pyramid_webassets 
    # registers a static view with default settings. Since we register our own
    # static views with custom cache_max_age, we want those views to come first
    # (since the router goes in the order in which views are added).
    configure_db(config)
    configure_auth(config)
    configure_routes(config)
    configure_jinja(config)

    config.scan('.views')

    return config.make_wsgi_app()
