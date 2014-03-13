from __future__ import unicode_literals

import hashlib
import urllib
import urlparse


def hash_url(url):
    normalized = normalize_url(url)
    hashed = md5(normalized)

    return hashed


def md5(unicode_string):
    """ Unicode-safe version of hashlib.md5 """

    hashed = hashlib.md5(unicode_string.encode('utf-8')).hexdigest()
    return hashed


def normalize_url(url):
    parsed = urlparse.urlparse(url) 

    # Sort the query string alphabetically
    qsl = urlparse.parse_qsl(parsed.query)
    qsl.sort(key=lambda x: x[0])
    qs_sorted = urlencode(qsl)

    new_parsed = urlparse.ParseResult('http', parsed.netloc, parsed.path, 
                                      parsed.params, qs_sorted, parsed.fragment)
    normalized = new_parsed.geturl()

    return normalized


def urlencode(data):
    """ Unicode-safe version of urllib.urlencode """
    if isinstance(data, dict):
        tuples = list(data.iteritems())
    else:
        tuples = data

    encoded_data = [] 
    for k, v in tuples:
        enc_k = unicode(k).encode('utf-8')
        enc_v = unicode(v).encode('utf-8')
        encoded_data.append((enc_k, enc_v))

    return urllib.urlencode(encoded_data)
