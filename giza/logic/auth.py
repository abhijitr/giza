# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

def get_groups(user_id):
    groups = None # unknown/unauthed user

    """
    user = profile.get_user(user_id=user_id)
    if user:
        groups = _get_groups_for_user(user)
    """

    return groups


def is_admin(user):
    if not user: 
        return False

    groups = _get_groups_for_user(user)
    return 'g:admin' in groups


def is_editor(user):
    if not user:
        return False
        
    groups = _get_groups_for_user(user)
    return 'g:editor' in groups


def _get_groups_for_user(user):
    if user.username in ['admin', 'aznhacker52', 'noseseeker']:
        groups = ['g:admin']
    else:
        groups = []

    return groups