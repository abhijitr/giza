# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

# Name this whatever you want
class AppError(Exception):
    def __init__(self, code, errors):
        Exception.__init__(self)
        self.code = code
        if hasattr(errors, '__iter__'):
            self.errors = errors
        else:
            self.errors = [errors]

from . import account
from . import anal
from . import auth
from . import image
