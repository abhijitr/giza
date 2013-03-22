# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from pyramid.threadlocal import get_current_registry


def get_bucket_name():
    registry = get_current_registry()
    settings = registry.settings or {}
    bucket_name = settings.get('giza.image_bucket', 'bucket')
    return bucket_name


def get_serving_url(key, thumbnail_size=None):
    bucket_name = get_bucket_name()
    if thumbnail_size is not None:
        img_url = 'https://s3.amazonaws.com/{0}/thumbs/{1}/{2}.jpg'.format(bucket_name, thumbnail_size, key) 
    else:
        img_url = 'https://s3.amazonaws.com/{0}/{1}.jpg'.format(bucket_name, key)
    return img_url
