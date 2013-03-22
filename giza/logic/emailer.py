# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

import email
import requests
from pyramid.url import urlencode

from . import AppError
from . import deferred

def send_mail(sender='', to='', subject='', body='', replyto='', cc='', bcc='', html=''):
    deferred.defer(_send_mail_callback, sender, to, subject, body, replyto, cc, bcc, html)

def send_admin_email(sender='', subject='', body='<eom>'):
    send_mail(sender=sender, to='', subject=subject, body=body)

def _send_mail_callback(sender='', to='', subject='', body='', replyto='', cc='', bcc='', html=''):
    sender_parsed = email.Utils.parseaddr(sender)
    to_parsed = []
    
    if not to: 
        raise AppError(500, 'internal-error')

    def parse(recipient_string):
        recipients = recipient_string.split(';')
        return [email.Utils.parseaddr(r) for r in recipients]
    
    to_parsed = parse(to)
    replyto_parsed = parse(replyto) if replyto else None
    cc_parsed = parse(cc) if cc else None
    bcc_parsed = parse(bcc) if bcc else None

    _send_mail_sendgrid(sender_parsed, to_parsed, subject, body, replyto_parsed, cc_parsed, bcc_parsed, html)

def _send_mail_sendgrid(sender, to, subject, body, replyto=None, cc=None, bcc=None, html=None):
    base_url = 'https://sendgrid.com/api/mail.send.json'
    params = {
        'api_user': '',
        'api_key': '',
        'subject': subject,
        'text': body,
        'fromname': sender[0],
        'from': sender[1]
    }
    
    if html:
        params['html'] = html
    
    # Encode the simple stuff
    encoded_params = urlencode(params)

    # List of 'to' addresses
    encoded_params += '&' + urlencode([('toname[]', toname) for toname,_ in to])
    encoded_params += '&' + urlencode([('to[]', toaddr) for _,toaddr in to])

    if replyto:
        encoded_params += '&' + urlencode([('replyto', replyto[0][1])])
    
    if cc:
        encoded_params += '&' + urlencode([('ccname[]', ccname) for ccname,_ in cc])
        encoded_params += '&' + urlencode([('cc[]', ccaddr) for _,ccaddr in cc])

    if bcc:
        encoded_params += '&' + urlencode([('bccname[]', bccname) for bccname,_ in bcc])
        encoded_params += '&' + urlencode([('bcc[]', bccaddr) for _,bccaddr in bcc])
        
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(base_url, data=encoded_params, headers=headers, verify=False, timeout=10)
    retval = resp.json()
    if retval['message'] == 'error':
        logging.error('Error sending email: %s' % (',').join(retval['errors']))
