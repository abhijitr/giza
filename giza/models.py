# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging, pprint

from datetime import datetime
import json
from sqlalchemy import (
    desc,
    func,
    Column,
    Integer,
    Unicode,
    DateTime,
    Numeric,
    Enum,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    backref,
    relationship,
    scoped_session,
    sessionmaker
)
import sqlalchemy.types as types
from zope.sqlalchemy import ZopeTransactionExtension

# Main db session for use by the web front end. It has request scope, and
# the transaction commit/rollback is handled by Pyramid + transaction package.
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

# Unmanaged db session to allow for use outside of Pyramid. It has thread local
# scope, and the consumer is responsible for commit/rollback of the transaction.
UnmanagedDBSession = scoped_session(sessionmaker())

Base = declarative_base()

class JsonType(types.TypeDecorator):
    impl = types.Unicode 

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if not value:
            return None
        return json.loads(value)


class TimestampMixin(object):
    created = Column(DateTime, default=func.now(), nullable=False)


class User(TimestampMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    visitor_id = Column(Unicode, nullable=False)
    username = Column(Unicode, unique=True, nullable=False)
    username_display = Column(Unicode, nullable=False)
    email = Column(Unicode, unique=True)
    email_display = Column(Unicode)
    password = Column(Unicode, nullable=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.username_display = self.username.strip()
        self.username = self.username.strip().lower()
        self.email_display = self.email.strip() if self.email else None
        self.email = self.email.strip().lower() if self.email else None


def populate():
    try:
        session = DBSession()
        admin = User('admin', 'admin@pickie.com', 'foobar')
        session.add(admin)
        session.flush()
    except IntegrityError:
        # already created
        pass


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
