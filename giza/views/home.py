# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint, os

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPMovedPermanently
from pyramid.response import FileResponse
from pyramid.renderers import render
from pyramid.security import forget, remember

from . import base
from .. import logic
from .. import formatters
from ..utils import reqparse as rp


@view_config(
    request_method='GET',
    route_name='home',
    renderer='home.html',
)
def requests_get(request):
    return {}
