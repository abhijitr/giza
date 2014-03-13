# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint
from HTMLParser import HTMLParser
from HTMLParser import HTMLParseError
import re
from slugify import slugify as pyslugify


def clean_str(the_str):
    return re.sub("[^a-zA-Z0-9.,:/;\-!?$ ]","",the_str)


def urlize(text, trim_url_limit=None):
    from jinja2.runtime import Markup
    from jinja2.filters import urlize as jinja_urlize

    return jinja_urlize(Markup(text), trim_url_limit=trim_url_limit)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    """ removes tags and leaves just text from html """
    s = MLStripper()
    s.feed(html)
    return s.get_data()
    

def slugify(text):
    return pyslugify(text)
