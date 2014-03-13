# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from .common import * 

giza['host'] = ''
giza['image_hosts'] = []
giza['image_bucket'] = ''
giza['require_https'] = False
giza['js_filters'] = 'requirejs,uglifyjs'

# Logging tweaks
giza['logging']['handlers']['syslog']['class'] = 'logging.handlers.SysLogHandler'
giza['logging']['handlers']['syslog']['address'] = '/dev/log'
