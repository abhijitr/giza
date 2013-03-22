# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import os
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

giza = dict(
    debug = False,
    auth_cookie = 'auth_1',
    authn_secret = 'my_auth_secret',
    session_cookie = 'session_1',
    session_secret = 'my_session_secret',
    enable_queues = True,
    ga_key = '',
    image_bucket = '',
    mixpanel_tokens = dict(
        default = ''
    ),
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