# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, datetime
import simplejson as json

from .. formatters import (
    base as base_formatter
)
from ..data import constants
from .. utils import url_for

def app_scaffold_data(request, command=None, command_args=None, extra_data=None,
    meta_data=None, attach_container=True):
    settings = request.registry.settings

    """
    user_data = user_formatter.format_detail(request, request.current_user, None)\
        if request.current_user else {}
    """
    user_data = {}
    
    experiments = {}

    img_hosts = settings['giza.image_hosts']

    data = {
        'VERSION': settings['giza.server_version'],
        'IMAGE_HOSTS': img_hosts, 
        'USER_DATA': user_data,
        'MODULES': settings['giza.modules'],
        'EXPERIMENTS': experiments
    }

    if command:
        data.update({'COMMAND': command})
    if command_args:
        data.update({'COMMAND_ARGS': command_args})
    if extra_data:
        data.update(extra_data)
  
    return dict(
        embed_data=json.dumps(data, indent=' '),
        data=data,
        base=base_formatter.format(request),
    )
