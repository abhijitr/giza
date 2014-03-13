# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import stripe

from ..logic import AppError

from pyramid.threadlocal import get_current_registry

logger = logging.getLogger(__name__)

class StripeError(Exception):
    def __init__(self, message='', code=0):
        Exception.__init__(self, message)
        self.code = code

    def __repr__(self):
        return 'StripeError({0}, {1})'.format(self.code, self.message)

def create_customer(stripe_token, description):
    registry = get_current_registry()
    stripe.api_key = registry.settings['giza.stripe_secret_key']

    try:
        customer = stripe.Customer.create(
            card=stripe_token,
            description=description
        )

        return customer

    except stripe.CardError, e:
        # Possibly a Decline
        body = e.json_body
        err  = body['error']
        
        raise AppError(400, 'card-error', parameter=err['message'])

    except stripe.InvalidRequestError, e:
        # Invalid Parameters
        raise AppError(400, 'bad-request')

    except stripe.AuthenticationError, e:
        # Possible Problem With Api Key
        raise AppError(400, 'bad-request')

    except stripe.StripeError, e:
        # Raise Error
        body = e.json_body
        err  = body['error']

        raise AppError(400, 'bad-request', parameter=err['message'])
        
    except Exception, e:

        pass

def charge_customer(amount, customer_uid, currency="usd"):
    registry = get_current_registry()
    stripe.api_key = registry.settings['giza.stripe_secret_key']

    try:
        charge = stripe.Charge.create(
            amount = amount,
            currency = currency,
            customer = customer_uid
        )
        return charge

    except stripe.CardError, e:
        # Possibly a Decline
        body = e.json_body
        err  = body['error']
        
        raise AppError(400, 'card-error', parameter=err['message'])

    except stripe.InvalidRequestError, e:
        # Invalid Parameters
        raise AppError(400, 'bad-request')

    except stripe.AuthenticationError, e:
        # Possible Problem With Api Key
        raise AppError(400, 'bad-request')

    except stripe.StripeError, e:
        # Raise Error
        body = e.json_body
        err  = body['error']

        raise AppError(400, 'bad-request', parameter=err['message'])
        
    except Exception, e:

        pass