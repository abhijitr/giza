# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import os
import sys

root = os.path.dirname(os.path.dirname(__file__))

pyramid = dict(
    reload_templates = False,
    debug_authorization = False,
    debug_notfound = False,
    debug_routematch = False,
    debug_templates = False,
    default_locale_name = 'en',
    includes = 'pyramid_tm', 
)

# pyramid_webassets expects a string instead of boolean for these
webassets = dict(
    base_dir = root + '/static',
    base_url = '/static',
    debug = 'False', 
    jst_compiler = 'Handlebars.compile',
    auto_build = 'True',
    versions = 'hash',
    cache = 'True',
)

celery = dict(
    broker_url = '',
    celeryd_hijack_root_logger = False
)

giza = dict(
    app_name = os.environ.get('app_name', ''),
    host = '',
    image_bucket = '',
    image_hosts = [],
    shoppt_image_hosts = [],
    image_domain = '',
    scrape_bucket = '',
    search_host = '',
    app_version = 0,
    server_version = '',
    debug = False,
    emulate_app = False,
    require_https = False,
    auth_cookie = 'auth_1',
    authn_secret = 'my_auth_secret',
    session_cookie = 'session_1',
    session_secret = 'my_session_secret',
    session_activity_timeout = 60 * 30,
    ga_key = os.environ.get('ga_key', ''),
    shoppt_ga_key = os.environ.get('shoppt_ga_key', ''),
    mixpanel_tokens = dict(
        default = os.environ.get('mixpanel_token', ''),
        ignore_mixpanel = '' 
    ),
    aws_key = os.environ.get('aws_key', ''),
    aws_secret = os.environ.get('aws_secret', ''),
    fb_key = os.environ.get('fb_key', ''),
    fb_secret = os.environ.get('fb_secret', ''),
    sendgrid_user = os.environ.get('sendgrid_user', ''),
    sendgrid_key = os.environ.get('sendgrid_key', ''),
    olark_id = os.environ.get('olark_id', ''),
    stripe_public_key = os.environ.get('stripe_public_key', ''),
    stripe_secret_key = os.environ.get('stripe_secret_key', ''),
    solr_host = os.environ.get('solr_host', ''),
    solr_secret = os.environ.get('solr_secret', ''),
    urban_airship_key = os.environ.get('urban_airship_key', ''),
    urban_airship_secret = os.environ.get('urban_airship_secret', ''),
    js_filters = 'requirejs,uglifyjs',
    clear_asset_cache = False,
    enable_file_watcher = False,
    modules = dict(
        concierge = False,
        search = False,
        faves = True,
        shop = False,
        bottom_nav = False,
        related = False,
        mentions = False,
        flagging = False,
        chat = True
    )
)

jinja2 = dict( 
    directories = 'giza:templates'
)

sqlalchemy = dict(
    url= ''
)

sentry = dict(
    dsn = ''
)

if giza.get('app_name'):
    giza['app_data_path'] = '/var/lib/{0}/data'.format(giza['app_name'])
else:
    giza['app_data_path'] = 'etc/data'
giza['cleaver_backend'] = 'sqlite:///{0}/experiment.data'.format(giza['app_data_path'])

giza['logging'] = { 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'default': {
            'format': 'app[%(process)d]: at=%(levelname)s mod=%(name)s %(message)s'
        }
    },
    'loggers': { 
        '': { 
            'level': 'INFO',
            'handlers': ['console']
        },
        'celery': {
            'level': 'INFO',
            # propagate to root handler
        },
        'worker': {
            'level': 'DEBUG',
            # propagate to root handler
        },
        'giza': { 
            'level': 'INFO',
            # propagate to root handler
        },
        'giza.perf': { 
            'level': 'DEBUG',
            # propagate to root handler
        },
        'giza.logic.anal': {
            'level': 'INFO',
            'handlers': ['syslog'],
            'propagate': False
        },
        'sqlalchemy.engine': { 
            'level': 'WARNING',
            # propagate to root handler
        },
        'psycopg2': { 
            'level': 'WARNING',
            # propagate to root handler
        },
        'pyramid_rewrite': {
            'level': 'WARNING',
        },
        'sentry.errors': { 
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False
        },
    },
    'handlers': {
        # Note: console output will also go to syslog
        'console': { 
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default'
        },
        # For skipping console and going straight to syslog
        'syslog': { 
            'level': 'INFO',
            'class': 'logging.NullHandler',
            'formatter': 'default'
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.handlers.logging.SentryHandler',
            'args': ('',),
            'formatter': 'default'
        }
    }
}
