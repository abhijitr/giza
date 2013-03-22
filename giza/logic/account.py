# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import hashlib
import random
import re
import time

from . import (
    AppError,
    emailer
)
from ..data import constants
from ..models import (
    DBSession,
    User,
)

def get_hexdigest(algo, salt, raw_password):
    """ partial port of Django's get_hexdigest. """
    if algo == 'sha1':
        return hashlib.sha1((salt + raw_password).encode('utf-8')).hexdigest()
    raise ValueError('Unsupported algorithm')

def generate_password(raw_password):
    algo = 'sha1'
    salt = get_hexdigest(algo, unicode(random.random()), unicode(random.random()))[:5]
    hsh = get_hexdigest(algo, salt, raw_password)
    return '%s$%s$%s' % (algo, salt, hsh)

def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    if not enc_password:
        return False
    algo, salt, hsh = enc_password.split('$')
    return hsh == get_hexdigest(algo, salt, raw_password)

def create(username, email, password, visitor_id):
    u_lowered = username.lower().strip()
    e_lowered = email.lower().strip()

    if re.search('[^A-Za-z0-9]', u_lowered):
        raise AppError(400, 'username-invalid-chars')

    if len(u_lowered) < 3:
        raise AppError(400, 'username-invalid')

    if u_lowered in constants.USERNAME_BLACKLIST:
        raise AppError(400, 'username-invalid')

    session = DBSession()
    existing = session.query(User)\
                      .filter((User.username == u_lowered) | 
                              (User.email == e_lowered) | 
                              (User.visitor_id == visitor_id))\
                      .first()
    if existing:
        if existing.username == u_lowered:
            if existing.type == 'shell':
                raise AppError(400, 'username-unclaimed')
            raise AppError(400, 'username-taken')
        if existing.email == e_lowered:
            raise AppError(400, 'email-taken')

    if not visitor_id or existing and (existing.visitor_id == visitor_id):
        # Make a minimal effort to prevent duplicate visitor_ids. This can
        # happen if the same user makes multiple accounts in the same session. 
        visitor_id = hashlib.md5(str(random.random())).hexdigest()

    if len(password) < 5:
        raise AppError(400, 'password-too-short')

    hashed = generate_password(password)
    user = User(username=username, email=email, password=hashed, visitor_id=visitor_id)
    session.add(user)
    session.flush()

    emailer.send_admin_email(subject='{0} just joined!'.format(username))

    return user

def login(login, password):
    l_lowered = login.lower()

    session = DBSession()
    existing = session.query(User).filter(
        (User.username == l_lowered) | (User.email == l_lowered)).first()

    if not existing:
        raise AppError(400, 'login-not-found')

    if existing.type == 'shell':
        raise AppError(400, 'username-unclaimed')

    match = check_password(password, existing.password)
    if not match:
        raise AppError(400, 'password-incorrect')

    return existing

def get_password_recovery_token(username):
    session = DBSession()
    user = session.query(User).filter_by(username=username).first()
    if not user:
        raise AppError(400, 'username-not-found')
        
    timestamp = str(int(time.time()) / 86400) # days since epoch
    hsh = get_hexdigest('sha1', timestamp, user.password)
    token = '%s|%s' % (hsh, timestamp)
    return user, token

def reset_password(username, token, new_password):
    session = DBSession()
    user = session.query(User).filter_by(username=username).first()
    if not user:
        raise AppError(400, 'username-not-found')

    components = token.split('|')
    if len(components) != 2:
        raise AppError(400, 'token-invalid')

    try:
        timestamp = int(components[1])
    except ValueError:
        raise AppError(400, 'token-invalid')

    current = int(time.time()) / 86400
    if current - timestamp > 30:
        # expires in 30 days
        raise AppError(400, 'token-invalid')

    hsh = components[0]
    if get_hexdigest('sha1', str(timestamp), user.password) != hsh:
        raise AppError(400, 'token-invalid')

    # OK!! we have a valid token
    new_hash = generate_password(new_password)
    user.password = new_hash
    user.type = 'normal'
    session.flush()

    return user
