# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint


def check_param(key, kwargs):
    return key in kwargs


def set_param(to_update, key, kwargs):
    if check_param(key, kwargs):
        if isinstance(to_update, dict):
            to_update[key] = kwargs[key]
        else:
            setattr(to_update, key, kwargs[key])
