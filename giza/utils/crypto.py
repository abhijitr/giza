# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import hashlib
from passlib.context import CryptContext
from passlib.hash import bcrypt
import random
import time


crypt_context = CryptContext(
    schemes=[str('django_bcrypt'), str('django_salted_sha1')],
    default=str('django_bcrypt'),
    deprecated=str('django_salted_sha1'),
    django_bcrypt__default_rounds=12
)


def generate_random_token(algo='md5'):
    algo_func = getattr(hashlib, algo)
    return algo_func(str(random.random())).hexdigest()
    

def encrypt(secret):
    return crypt_context.encrypt(secret)


def verify_and_update(secret, hash):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    return crypt_context.verify_and_update(secret, hash)


def generate_secret_token(secret, ttl=86400*30):
    if not secret:
        raise ValueError('secret missing')

    expires_at = str(int(time.time() + ttl)) # unix timestamp 

    # call bcrypt directly so there's no leading "bcrypt" in the hash
    hsh = bcrypt.encrypt(secret + expires_at)
    token = '%s|%s' % (hsh, expires_at)
    return token


def check_secret_token(secret, token):
    if not secret:
        raise ValueError('secret missing')

    components = token.split('|')
    if len(components) != 2:
        return False

    hsh, expires_at = components

    try:
        expires_at = int(expires_at)
    except ValueError:
        return False

    current = int(time.time())
    if current > expires_at:
        return False

    if not bcrypt.verify(secret + str(expires_at), hsh):
        return False

    return True
