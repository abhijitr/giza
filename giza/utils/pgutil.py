# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from psycopg2.extras import LoggingConnection, LoggingCursor
from pyramid import threadlocal
from sqlalchemy.engine import url
import time


# Based on MinTimeLoggingConnection in psycopg2.extras
class PerfLoggingConnection(LoggingConnection):
    def initialize(self, logobj, mintime=0):
        LoggingConnection.initialize(self, logobj)

    def filter(self, msg, curs):
        elapsed = (time.time() - curs.timestamp) * 1000
        request = threadlocal.get_current_request()
        request_id = getattr(request, 'id', '-') if request else '-' 
        cleaned_msg = ' '.join([l.strip() for l in msg[:30].splitlines()]) 

        return "query=\"{0}\" service={1}ms rid={2}".format(cleaned_msg, int(elapsed), request_id)

    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', PerfLoggingCursor)
        return LoggingConnection.cursor(self, *args, **kwargs)


class PerfLoggingCursor(LoggingCursor):
    def execute(self, query, vars=None):
        self.timestamp = time.time()
        return LoggingCursor.execute(self, query, vars)

    def callproc(self, procname, vars=None):
        self.timestamp = time.time()
        return LoggingCursor.execute(self, procname, vars)


def create_logging_connection(dsn):
    logger = logging.getLogger('giza.perf')
    conn = PerfLoggingConnection(dsn)
    conn.initialize(logger)
    return conn
