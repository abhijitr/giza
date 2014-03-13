# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import re
import urlparse
import json
import decimal

from ..logic import AppError


class Namespace(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
    def __setattr__(self, name, value):
        self[name] = value


class Invalid(Exception):
    def __init__(self, reason, data=None):
        Exception.__init__(self)
        self.reason = reason
        self.data = data


def Required(allow_blanks=False, reason='parameter-required'):
    # Maybe a => a
    def converter(data):
        if data is None:
            raise Invalid(reason, data)
        if not allow_blanks and isinstance(data, basestring) and not data.strip():
            raise Invalid(reason, data)
        return data

    return converter


def Default(default, allow_blanks=False, reason=None):
    # Maybe a => a
    def converter(data):
        if data is None:
            return default
        if not allow_blanks and isinstance(data, basestring) and not data.strip():
            return default
        return data

    return converter

def Boolean(reason='parameter-invalid'):
    # Maybe a => Maybe unicode
    def converter(data):
        if data is None or data == "":
            return None 
        try:
            output = json.loads(data.lower())
        except ValueError:
            raise Invalid(reason, data)
        return output

    return converter

def Choice(*choices, **kwargs):
    # Maybe a => Maybe choices
    def converter(data):
        if data is None or data == "":
            return data
        if data not in choices:
            raise Invalid(kwargs.get('reason', 'parameter-invalid'), data)
        return data

    return converter


def Unicode(reason='parameter-invalid'):
    # Maybe a => Maybe unicode
    def converter(data):
        if data is None or data == "":
            return data
        try:
            output = unicode(data)
        except ValueError:
            raise Invalid(reason, data)
        return output

    return converter


def Json(reason='parameter-invalid'):
    # Maybe a => Maybe dict 
    def converter(data):
        if data is None or data == "":
            return None 
        try:
            output = json.loads(data)
        except ValueError:
            raise Invalid(reason, data)
        return output

    return converter


def Length(min=None, max=None, reason='parameter-outofrange'):
    # Maybe unicode => Maybe unicode
    def converter(data):
        if data is None or data == "":
            return data
        if (min is not None and len(data) < min) or\
           (max is not None and len(data) > max):
           raise Invalid(reason, data)
        return data

    return converter


def Integer(reason='parameter-invalid'):
    # Maybe a => Maybe int
    def converter(data):
        if data is None or data == "":
            return None
        try:
            output = int(data)
        except ValueError:
            raise Invalid(reason, data)
        return output

    return converter

def Decimal(reason='parameter-invalid'):
    def converter(data):
        if data is None:
            return None
        try:
            output = decimal.Decimal(data)
        except InvalidOperation:
            raise Invalid(reason, data)
        return output

    return converter


def Float(reason='parameter-invalid'):
    # Maybe a => Maybe float
    def converter(data):
        if data is None or data == "":
            return None
        try:
            output = float(data)
        except ValueError:
            raise Invalid(reason, data)
        return output

    return converter


def Range(min=None, max=None, reason='parameter-outofrange'):
    # Maybe int => Maybe int
    def converter(data):
        if data is None or data == "":
            return data
        if (min is not None and data < min) or\
           (max is not None and data > max):
           raise Invalid(reason, data)
        return data
    return converter


def Regex(pattern, flags=0, reason='parameter-invalid'):
    # Maybe unicode => Maybe unicode
    def converter(data):
        if data is None:
            return None
        if not re.match(pattern, data, flags):
            raise Invalid(reason, data)
        return data
    return converter


def Email(reason='email-invalid'):
    return Regex('[^ @]+@[^ @]+\.[^ @]+|^$', flags=re.IGNORECASE, reason=reason)


def Url(reason='url-invalid'):
    def converter(data):
        if data is None or data == "":
            return data
        parsed = urlparse.urlparse(data)
        if not parsed.netloc:
            raise Invalid(reason, data)
        return data
    return converter


def File(reason='parameter-invalid'):
    def converter(data):
        if data is None or data == "":
            return data
        if not hasattr(data, 'file'):
            raise Invalid(reason, data)
        return data
    return converter


class Get(object):
    """Pulls values off the request in the provided location.
    """
    def __init__(self, locations=('params',), multiple=False, separator=','):
        self.locations = locations
        self.multiple = multiple
        self.separator = separator

    def __call__(self, request, name):
        values = []
        for l in self.locations:
            source = getattr(request, l, None)
            if source is not None and name in source:
                # Account for MultiDict and regular dict
                if hasattr(source, "getall"):
                    values = source.getall(name)
                else:
                    values = [source.get(name)]                

                break

        if self.multiple:
            result = []
            for val in values:
                result.extend([v for v in val.split(self.separator) if v])
            values = result
            return values
        else:
            return values[-1] if len(values) else None


"""
DEFAULT_SIGNATURE = {
    'fields': {'type': str, 'multiple': True, 'default': ['default']},
    'format': {'type': str, 'choices': ('json',), 'default': 'json'},
} 
"""
DEFAULT_SIGNATURE = {}

def _apply(value, pipeline):
    out = value
    for func in pipeline:
        out = func(out)
    return out

def parse(request, signature):
    sig = {}
    sig.update(DEFAULT_SIGNATURE)
    sig.update(signature)

    namespace = Namespace()

    errors = []
    for param, validators in sig.iteritems():
        getter = validators[0]
        if isinstance(getter, Get):
            pipeline = validators[1:]
        else:
            getter = Get(locations=('matchdict', 'params'), multiple=False)
            pipeline = validators

        data = getter(request, param)

        if getter.multiple:
            values = []
            for datum in data:
                try:
                    values.append(_apply(datum, pipeline))
                except Invalid as i:
                    errors.append({'code': 400, 'reason': i.reason, 'parameter': param, 'data': datum})
            namespace[param] = values
        else:
            try:
                namespace[param] = _apply(data, pipeline)
            except Invalid as i:
                errors.append({'code': 400, 'reason': i.reason, 'parameter': param, 'data': data})

    if len(errors):
        raise AppError(errors=errors)

    return namespace
