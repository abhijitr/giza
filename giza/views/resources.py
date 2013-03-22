# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    authenticated_userid
)

class Root(object):
    __acl__ = [
        (Allow, Authenticated, 'create'),
        (Allow, 'g:editor', 'edit'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]
    __name__ = ''
    __parent__ = None

    def __init__(self, request):
        self.request = request
