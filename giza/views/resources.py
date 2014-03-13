# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint
from pyramid.threadlocal import get_current_registry
from pyramid.request import Request

from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    authenticated_userid,
    Everyone
)

from .. import logic


class Root(object):
    __acl__ = [
        (Allow, Authenticated, 'read'),
        (Allow, 'g:editor', 'edit'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]
    __name__ = ''
    __parent__ = None

    def __init__(self, request):
        self.request = request


class GizaRequest(Request):
    # HACK: we need to get the host and scheme from the registry, but this is 
    # not available at the time GizaRequest.blank() is called, so we wait till
    # the registry is added to the request and then set the host and scheme
    def __setattr__(self, name, value):
        if name == 'registry': 
            if value.settings.get('giza.require_https'):
                self.scheme = "https"
            else:
                self.scheme = "http"
            self.host = value.settings.get('giza.host')
        return super(GizaRequest, self).__setattr__(name, value)
