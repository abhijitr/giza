# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import base64
import datetime
import json
import re
import requests
import time

from . import auth
from . import deferred

# Whitelist of accepted events per mixpanel project. You must add
# an entry here if you are adding a new event. Hopefully this will encourage
# us to keep a sane naming convention.
event_whitelists = {
    'default': frozenset([
        'account-login',
        'account-login-submit',
        'account-login-error',
        'account-logout-submit',
        'account-signup',
        'account-signup-submit',
        'account-signup-error',
        'account-password-recover',
        'account-password-recover-submit',
        'account-password-recover-error',
        'account-password-reset',
        'account-password-reset-submit',
        'account-password-reset-error',

        'landing',
    ])
}

# Blacklist of crawlers to ignore
CRAWLER_PATTERN = re.compile(
    '|'.join([
        'Googlebot', 'Yammybot', 'Openbot', 'Yahoo', 'Slurp', 'bingbot',
        'msnbot', 'ia_archiver', 'Lycos', 'Scooter', 'AltaVista', 'Teoma', 
        'Gigabot', 'Googlebot-Mobile', 'BaiduSpider', 'ScoutJet', 'DuckDuckBot' 
    ]),
    re.IGNORECASE
)


def track_event(request, event, properties=None, user=None, mixpanel_project='default'):
    # user can be overridden in cases where there is no user on the request
    # object (namely when you just logged in/signed up)
    user = user or request.current_user

    if not _should_track(request, user):
        return

    track_user(request, user)
   
    # Fill in the basics
    properties = properties.copy() if properties else {}
    properties['event_name'] = event
    properties.update(_get_common_properties(request, user, mixpanel_project))
  
    # Queue it up
    deferred.defer(_track_event_callback, properties)


def track_client_event(request, properties, mixpanel_project='default'):
    user = request.current_user

    if not _should_track(request, user):
        return

    track_user(request, user)

    properties = properties.copy() if properties else {}
    properties.update(_get_common_properties(request, user, mixpanel_project))

    # this stuff is meaningless in this context
    del properties['url']
    del properties['referer']
      
    # No need to do deferred here since this should already be getting called asynchronously
    _track_event_callback(properties)


def track_external(request, data, mixpanel_project='default'):
    user = request.current_user

    if not _should_track(request, user):
        return

    track_user(request, user)
   
    properties = json.loads(base64.b64decode(data))
    properties.update(_get_common_properties(request, user, mixpanel_project))

    # URL is meaningless in this context
    del properties['url']
    if 'query_string' in properties:
        del properties['query_string']

    # No need to do deferred here since this should already be getting called asynchronously
    _track_event_callback(properties)


def tracking_url(request, event, properties=None, redirect=None):
    properties = properties.copy() if properties else {}
    properties['event_name'] = event
    data = base64.b64encode(json.dumps(properties))

    params = {'data': data}
    if redirect:
        params['redirect'] = redirect

    endpoint = request.route_path('track', _query=params)
    return endpoint


def track_user(request, user, properties=None, mixpanel_project='default'):
    """
    Set properties for a user in mixpanel

    @param request: The request 
    @param user: The user
    @param properties: A dictionary of key-value pairs that we want to also
        track beyond the defaults
    See https://mixpanel.com/docs/people-analytics/people-http-specification-insert-data
    @return response from mixpanel 
    """
    
    if not user:
        return
    
    params = {}
    params['$token'] = request.registry.settings['giza.mixpanel_token_%s' % mixpanel_project]
    params['$distinct_id'] = user.visitor_id
    params['$ip'] = request.environ['REMOTE_ADDR'] 

    created = user.created.isoformat() if user.created else None

    params['$set'] = {
        '$username':user.username,
        '$email':user.email,
        '$created':created,
        'user_id':user.id,
    }
    
    if properties:
        params['$set'].update(properties)

    if not params['$token']:
        # Debug mode, just bail out
        return

    deferred.defer(_call_mixpanel, 'engage', params)

    
def _should_track(request, user=None):
    # Don't track admins and editors
    if request.session.get('impersonator_id'):
        return False
    if auth.is_admin(user) or auth.is_editor(user):
        return False

    ua = request.environ.get('HTTP_USER_AGENT', '') 
    if re.search(CRAWLER_PATTERN, ua):
        return False

    return True


def _track_event_callback(params):
    if 'url' in params and params['url']:
        params['url'] = params['url'][:500]
    if 'referer' in params and params['referer']:
        params['referer'] = params['referer'][:500]
    if 'user_id' in params and params['user_id']:
        params['user_id'] = int(params['user_id'])

    mixpanel_project = None 
    if 'mixpanel_project' in params:
        mixpanel_project = params['mixpanel_project']
        del params['mixpanel_project']

    # check if it's a valid event
    whitelist = event_whitelists[mixpanel_project]
    event_name = params['event_name']
    if event_name not in whitelist:
        logging.warn('unknown event type %s, discarding', event_name)
        return

    """
    # Store it on our side
    usage_event = events.UsageEvent(**params)
    usage_event.put()
    """

    # Send to mixpanel
    if mixpanel_project:
        event = params['event_name']
        del params['event_name']

        # This name will show up in the Mixpanel 'Streams' view
        if 'username' in params:
            params['mp_name_tag'] = params['username']

        if not params['token']:
            # Debug mode, just bail out
            return

        props = {"event": event, "properties": params}

        _call_mixpanel('track', props)


def _call_mixpanel(endpoint, properties):
    data = base64.b64encode(json.dumps(properties))
    url = "http://api.mixpanel.com/{0}/?data={1}".format(endpoint, data)

    resp = requests.get(url, timeout=30)
    logging.info('Response from mixpanel: %r', resp.status_code)


def _get_common_properties(request, user, mixpanel_project):
    properties = {}

    # Basics
    properties['time'] = int(time.time())
    properties['ip'] = request.environ['REMOTE_ADDR'] 
    properties['referer'] = request.environ.get('HTTP_REFERER', None)
    properties['url'] = request.environ['PATH_INFO']
    if 'QUERY_STRING' in request.environ:
        properties['query_string'] = request.environ['QUERY_STRING']

    # Use the visitor_id if possible, or fall back on the session_id (which 
    # becomes the visitor_id if the user ends up signing up)
    properties['distinct_id'] = user.visitor_id if user else request.session.get('session_id')

    # User data
    if user:
        properties['username'] = user.username
        properties['user_id'] = user.id

        # Assign the user to two cohorts: one for the day they joined, and one
        # for the Sunday before they joined.
        cohort_date = user.created or datetime.datetime.fromtimestamp(0)
        cohort_week = cohort_date - datetime.timedelta(days=cohort_date.weekday())
        properties['cohort_date'] = cohort_date.strftime('%Y%m%d')
        properties['cohort_week'] = cohort_week.strftime('%Y%m%d')

    """
    # Data about active experiments the user is part of
    experiments = gae_bingo.find_participating_experiments_for_user()
    for name, alternative in experiments.iteritems():
        prop_name = "x:%s" % name
        properties[prop_name] = alternative
    """

    if mixpanel_project:
        properties['mixpanel_project'] = mixpanel_project
        properties['token'] = request.registry.settings['giza.mixpanel_tokens'][mixpanel_project]

    return properties


"""
TODO: port this from app engine

def _track_last_visit(request):
    user = request.current_user
    if not user:
        return

    last_visit = user.date_visited or datetime.datetime.fromtimestamp(0)
    now = datetime.datetime.now()
    delta = now - last_visit
    if (delta.days <= 0 and delta.seconds <= 60):
        # already updated recently, just bail
        return
   
    deferred.defer(_do_track_last_visit, , 
                   _queue='track-click')
    

def _do_track_last_visit(user_key):
    def txn():
        user = db.get(user_key)
        if user:
            user.date_visited = datetime.datetime.now()
            user.save()
        return user
    the_user = db.run_in_transaction(txn)
    
    track_mixpanel_user(the_user)
"""
