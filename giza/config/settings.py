# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

def load_settings(global_config, local_config):
    config_module = global_config.get('config', 'dev')
    logging.info('loading config: ' + config_module)

    # load the settings in the .ini
    settings = dict(local_config)

    # from the config module, get all module-level variables that are dicts
    mod = __import__(config_module, globals(), locals(), [], 1)
    keys = [k for k in dir(mod) if not k.startswith('__')]
    values = [getattr(mod, k) for k in keys]
    dicts = [(k, v) for k, v in zip(keys, values) if isinstance(v, dict)]

    # add the settings specified in the config module
    for k, v in dicts:
        for subkey, val in v.iteritems():
            settings['%s.%s' % (k, subkey)] = val

    logging.info('starting config:\n' + pprint.pformat(settings))

    return settings
