# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint
import os

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.response import FileResponse
from pyramid.httpexceptions import HTTPFound

from .. import logic


@view_config(
    request_method='GET',
    route_name='landing',
    renderer='landing.html'
)
def get_landing(request):
    user = request.current_user
    if user:
        return HTTPFound(
            location = request.route_path('feed')
        )

    logic.anal.track_event(request, 'landing')

    return {'landing': True}


# Eh? need a better place for this...
@view_config(
    request_method='GET',
    route_name='track',
)
def get_track(request):
    redirect = request.params.get('redirect')
    data = request.params.get('data')

    api.anal.track_external(request, data)

    return HTTPFound(
        location = redirect 
    )
