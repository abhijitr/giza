# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import os

from .common import * 

pyramid['reload_templates'] = True

giza['host'] = ''
giza['require_https'] = False
giza['image_hosts'] = []
giza['image_bucket'] = ''

giza['stripe_public_key'] = ''
giza['stripe_secret_key'] = ''
giza['js_filters'] = 'requirejs'     # temporarily remove uglify so we can debug production issues :P

# Logging tweaks
giza['logging']['handlers']['syslog']['class'] = 'logging.handlers.SysLogHandler'
giza['logging']['handlers']['syslog']['address'] = '/dev/log'
