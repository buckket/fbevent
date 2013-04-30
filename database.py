from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

import settings

Base = declarative_base()
engine = None
session = None



def init_db():
    global engine, session

    engine = create_engine(settings.DB_URI, echo=False)

    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    Base.metadata.create_all(bind=engine)


class Event(Base):
    __tablename__ = 'events'

    event = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    event_id = Column(String(32), unique=True)
    name = Column(String(256))
    description = Column(Text())
    start_time = Column(DateTime())
    end_time = Column(DateTime())
    location = Column(Text())


class Guest(Base):
    __tablename__ = 'guests'

    guest = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    fb_id = Column(String(32), unique=True)
    fb_name = Column(String(128))


class Inviter(Base):
    __tablename__ = 'inviter'

    inviter = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(128))


class GuestEvent(Base):
    __tablename__ = 'guest_event'

    guest_event = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)

    guest_id = Column('guest', Integer(unsigned=True), ForeignKey('guests.guest'))
    guest = relationship('Guest', backref=backref('events'))

    event_id = Column('event', Integer(unsigned=True), ForeignKey('events.event'))
    event = relationship('Event', backref=backref('guests'))

    status = Column(String(64))
    

class GuestInvites(Base):
    __tablename__ = 'guest_invites'

    guest_invites = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)

    invited_id = Column('invited', Integer(unsigned=True), ForeignKey('guest_event.guest_event'))
    invited = relationship('GuestEvent', backref=backref('invites'))

    inviter_id = Column('inviter', Integer(unsigned=True), ForeignKey('inviter.inviter'))
    inviter = relationship('Inviter', backref=backref('invited'))
