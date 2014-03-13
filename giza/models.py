# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from math import log
from datetime import datetime, timedelta
import simplejson as json
from sqlalchemy import (
    cast,
    desc,
    func,
    case,
    Column,
    Boolean,
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String, # Only to be used for strings of bytes 
    Unicode,
    UnicodeText,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import (
    ARRAY
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    backref,
    relationship,
    scoped_session,
    sessionmaker,
    validates
)
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import sqlalchemy.types as types
import urlparse
from zope.sqlalchemy import ZopeTransactionExtension

from giza.data import constants

# Main db session for use by the web front end. It has request scope, and
# the transaction commit/rollback is handled by Pyramid + transaction package.
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    #Uncomment to auto-generate db tables based on models.py
    #Base.metadata.create_all(engine)

#---------------
# Helpers 
#---------------
class TimestampMixin(object):
    created_date = Column(DateTime, default=func.now(), nullable=False)
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
