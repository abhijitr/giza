# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import random
from pyramid.view import view_config, forbidden_view_config
from pyramid.response import Response
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound, 
    HTTPSeeOther
)

from ..logic import AppError

CLIENT_ERROR_HEADINGS = [ 
    'Oops!'
]

SERVER_ERROR_HEADINGS = [
    'Well this is embarassing...',
]

ERROR_MESSAGES = {
}


def _translate_message(msg_id, params=None):
    tmpl = ERROR_MESSAGES.get(msg_id, 'Something went wrong')
    params = params or {}
    return tmpl.format(**params)


def _header_message(code):
    if code / 100 == 4:
        return random.choice(CLIENT_ERROR_HEADINGS)
    elif code / 100 == 5:
        return random.choice(SERVER_ERROR_HEADINGS)
    else:
        return ''


def translate_errors(e, params=None):
    params = params or {}

    msg_dict = {}
    if isinstance(e, AppError):
        error_code = e.code
        msg_dict = {'_api': e.errors}
    elif isinstance(e, dict):
        error_code = 400 # Assume it's the user's fault
        msg_dict = e
    else:
        raise ValueError('Expecting a dict or AppError')

    all_errors = []
    all_ids = []
    translated_errors = {}

    for k, msg_ids in msg_dict.iteritems():
        if isinstance(msg_ids, basestring):
            # Just one message
            all_ids.append(msg_ids)
            translated = [_translate_message(msg_ids, params)]
        else:
            # Iterate over the stuff
            all_ids.extend(msg_ids)
            translated = [_translate_message(msg_id, params) for msg_id in msg_ids]

        translated_errors[k] = translated
        all_errors.extend(translated)

    translated_errors['_'] = all_errors
    translated_errors['_heading'] = _header_message(error_code)
    translated_errors['_ids'] = all_ids

    return translated_errors


@forbidden_view_config()
def forbidden_view(request):
    if authenticated_userid(request):
        # user is already logged in, they are really forbidden
        return HTTPForbidden()

    return_url = '%s?%s' % (request.environ['PATH_INFO'], request.environ['QUERY_STRING'])

    url = request.route_url('signup', _query={'return_url': return_url})
    return HTTPSeeOther(url)
