# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from .common import * 

pyramid['reload_templates'] = True

giza['image_bucket'] = 'staging-bucket'

sqlalchemy['url'] = ''
sqlalchemy['url'] = 'postgresql+psycopg2://webapp:password@localhost:5432/giza'
