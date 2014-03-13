# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from .common import * 

pyramid['reload_templates'] = True
pyramid['includes'] = '\n'.join([
    'pyramid_tm',
    #'pyramid_debugtoolbar' # Currently doesn't play nicely with fancybox, see https://github.com/Pylons/pyramid_debugtoolbar/issues/38
])

# adjust for localhost
giza['host'] = ''
giza['image_hosts'] = []
giza['image_bucket'] = ''

# For debugging bliss
giza['debug'] = True
giza['enable_file_watcher'] = True 
giza['emulate_app'] = True 

# Webasset config
webassets['debug'] = 'True'
giza['clear_asset_cache'] = True 

# Put the following in your <me>.py if you want the web assets to get fully built
# but caches aggressively cleared:
#webassets['debug'] = 'False'
#giza['clear_asset_cache'] = True    

#Stripe Keys
giza['stripe_public_key'] = ''
giza['stripe_secret_key'] = ''

#Turn On/Off Modules
giza['modules'] = {
    'concierge' : True,
    'search' : False,
    'faves' : True,
    'shop' : False,
    'bottom_nav' : True,
    'related' : False,
    'mentions' : False,
    'flagging' : False,
    'chat': False,
    'sourceProfile': True
}

# Logging tweaks
giza['logging']['loggers']['']['level'] = 'DEBUG'
giza['logging']['loggers']['giza']['level'] = 'DEBUG'
giza['logging']['loggers']['sqlalchemy.engine']['level'] = 'WARN'
giza['logging']['loggers']['txn'] = {'level': 'WARN'}

sqlalchemy['url'] = 'sqlite://'

celery['broker_url'] = 'redis://localhost'
celery['celery_always_eager'] = True
celery['celery_eager_propagates_exceptions'] = True