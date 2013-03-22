# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from .common import * 

pyramid['reload_templates'] = True
pyramid['includes'] = '\n'.join([
    'pyramid_tm',
    'pyramid_debugtoolbar'
])

webassets['debug'] = 'True'

giza['debug'] = True
giza['enable_queues'] = False 
giza['image_bucket'] = 'dev-bucket'

sqlalchemy['url'] = 'postgresql+psycopg2://webapp:password@localhost:5432/giza'
