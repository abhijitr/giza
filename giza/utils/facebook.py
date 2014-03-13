# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import requests
from requests.exceptions import RequestException
import simplejson as json
import urllib
import urlparse

logger = logging.getLogger(__name__)


class FacebookError(Exception):
    def __init__(self, message='', code=0):
        Exception.__init__(self, message)
        self.code = code

    def __repr__(self):
        return 'FacebookError({0}, {1})'.format(self.code, self.message)


def get_oauth_url(api_key, redirect_uri, scope, state):
    args = {
        'client_id': api_key,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': state
    }
    url = 'https://www.facebook.com/dialog/oauth/?' + urllib.urlencode(args)
    return url


def get_access_token(verification_code, api_key, secret_key, redirect_uri):
    if not verification_code:
        raise ValueError('verification_code is required')

    args = {
        'client_id': api_key,
        'client_secret': secret_key,
        'code': verification_code,
        'redirect_uri': redirect_uri,
    }
    url = "https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(args)
    response = requests.get(url, timeout=20)
    content = response.content
    logger.info('get_access_token: oauth returned content="%s"', content)
    parsed = dict(urlparse.parse_qsl(content))
    access_token = parsed.get('access_token', None)
    if not access_token:
        raise FacebookError('FB Oauth returned bad response: %s' % content)

    return access_token


def get_long_lived_access_token(api_key, secret_key, access_token):        
    try:
        url = "https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(dict(client_id=api_key,
                                                                                   client_secret=secret_key,
                                                                                   fb_exchange_token=access_token,
                                                                                   grant_type="fb_exchange_token"))
        fetched = requests.get(url, timeout=20)
        
        #if we couldn't get a the long lived access token, return None
        if fetched.status_code != 200:
            logger.error('get_long_lived_access_token returned error: url="%s", content="%s"', url, fetched.content)
            return None 
        return fetched.content.replace("access_token=","").split("&")[0]
    except RequestException:
        logger.exception('get_long_lived_access_token failed: url="%s"', url)
        return None
        
    
def get_profile_info(id, access_token):
    """ gets the profile information for the user specified by id
    """
    try:
        url = "https://graph.facebook.com/" + str(id) + "?" +urllib.urlencode(dict(access_token=access_token))
        resp = requests.get(url, timeout=20)
        return json.loads(resp.content)
    except RequestException:
        logger.exception('get_profile_info failed: url="%s"', url)
        return None


def get_likes(id, access_token, limit=1000):
    """ gets the 'likes' information for the user specificed by id
    """

    url = "https://graph.facebook.com/" + str(id) + "/likes?" + urllib.urlencode(dict(access_token=access_token))
    url += "&limit=" + str(limit)
    likes = json.loads(requests.get(url=url, timeout=20).content)

    if 'data' in likes:
        return likes['data']
    else:
        return []
