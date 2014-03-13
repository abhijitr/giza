# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from urlparse import urljoin
import requests

solr_singelton = None


def initialize(host, secret):
    global solr_singelton
    url = 'http://%s/solr' % host
    solr_singelton = SolrConnection(url, secret)


def get_connection():
    return solr_singelton


class SolrConnection:
    def __init__(self, solr_url, secret):
        if solr_url[-1] != '/':
            url = solr_url + '/'
        else:
            url = solr_url 

        self._base_url = url
        self._secret = secret

    def dataimport(self, clean=False):
        endpoint = urljoin(self._base_url, 'dataimport')
        params = {'command': 'full-import', 'clean': 'true' if clean else 'false'}
        requests.get(endpoint, params=params, headers={'sauce': self._secret})

    def query(self, query, filter_query=None, fields=[], sort=None, offset=None, limit=None):
        params = {
            'q': unicode(query),
            'wt': 'json'
        }

        if filter_query:
            params['fq'] = unicode(filter_query)

        if sort:
            params['sort'] = sort

        if len(fields) > 0:
            params['fl'] = ','.join(fields)

        if offset:
            params['start'] = offset

        if limit:
            params['rows'] = limit

        # TODO(schmich): Handle errors (like Solr not running).
        r = requests.get(urljoin(self._base_url, 'select'), params=params, headers={'sauce': self._secret})
        return r.json()


class Query:
    def __init__(self):
        pass

    def __and__(self, other):
        if self.__class__ == Query:
            return other
        else:
            return And(self, other)

    def __or__(self, other):
        if self.__class__ == Query:
            return other
        else: 
            return Or(self, other)

    def __unicode__(self):
        return '*:*'

    def __str__(self):
        return unicode(self).encode('utf-8')


class Eq(Query):
    def __init__(self, field, value):
        self._field = field
        self._value = value

    def _format_value(self, value):
        if isinstance(value, basestring):
            if value.find(' ') >= 0 or value.find(':') >= 0:
                return self._quote(value)
            else:
                return value
        elif isinstance(value, tuple):
            if len(value) == 0:
                return '[* TO *]'
            elif len(value) == 1:
                return '[%s TO *]' % value[0]
            else:
                return '[%s TO %s]' % (value[0] or '*', value[1] or '*')
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, list):
            return '(%s)' % ' '.join([self._format_value(v) for v in value])
        elif isinstance(value, (int, long, float)):
            return str(value)
        else:
            return self._quote(str(value))

    def _quote(self, value):
        return '"%s"' % value.replace('"', r"\"")

    def __unicode__(self):
        return "%s:%s" % (self._field, self._format_value(self._value))


class And(Query):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def __unicode__(self):
        return "%s AND %s" % (self._left, self._right)


class Or(Query):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def __unicode__(self):
        return "%s OR %s" % (self._left, self._right)


class Group(Query):
    def __init__(self, expr):
        self._expr = expr

    def __unicode__(self):
        return "(%s)" % (self._expr)


class Not(Query):
    def __init__(self, expr):
        self._expr = expr

    def __unicode__(self):
        if isinstance(self._expr, Eq):
            return '-%s' % self._expr
        else:
            raise RuntimeError, 'Not is not supported for this type.'
