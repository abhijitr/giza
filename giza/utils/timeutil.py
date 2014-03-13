# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import datetime

def get_delta_summary(time1,time2=None):
    """for two datetimes, figure out difference in words (e.g. 1 day left, 30 seconds left etc.) """
    
    if not time2:
        time2 = datetime.datetime.utcnow()
        
    delta = time2 - time1
    if delta.days:
        if delta.days == 1:
            return "1 day"
        else:
            return unicode(delta.days) + " days"
    else:
        total_seconds = delta.seconds
        if total_seconds < 0:
            total_seconds = 0
        
        total_hours = total_seconds / 60 / 60
        if total_hours:
            if total_hours == 1:
                return "1 hour"
            else:
                return unicode(total_hours) + " hours"
        total_minutes = total_seconds / 60 
        if total_minutes:
            if total_minutes == 1:
                return "1 minute"
            else:
                return unicode(total_minutes) + " minutes"
        if total_seconds == 1:
            return "1 second"
        else:
            return unicode(total_seconds) + " seconds"