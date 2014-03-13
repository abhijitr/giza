# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from collections import namedtuple

ErrorDetail = namedtuple('ErrorDetail', 'code, reason, parameter, data')

class AppError(Exception):
    def __init__(self, code=400, reason='bad-request', parameter=None, data=None, errors=None):
        Exception.__init__(self)
        if errors:
            self.errors = [ErrorDetail(**e) for e in errors]
        else:
            err = ErrorDetail(code=code, reason=reason, parameter=parameter, data=data)
            self.errors = [err]

    @property
    def code(self):
        return self.errors[0].code

    @property
    def reason(self):
        return self.errors[0].reason

    @property
    def parameter(self):
        return self.errors[0].parameter

    @property
    def data(self):
        return self.errors[0].data
