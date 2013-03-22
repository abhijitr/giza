# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import hashlib
from pyramid.events import (
    NewRequest,
    subscriber
)
import random

@subscriber(NewRequest)
def on_before_render(event):
    """ Ensure there's a session id assigned. """
    session = event.request.session
    if not 'session_id' in session:
        session['session_id'] = hashlib.md5(str(random.random())).hexdigest()
