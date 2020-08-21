from sqlalchemy import (
    Column,
    Boolean,
    Index,
    Integer,
    String,
    DateTime,
    Date,
    Time,
    ForeignKey,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from sqlalchemy.schema import (
    CheckConstraint,
    UniqueConstraint,
    )

from zope.sqlalchemy import ZopeTransactionExtension

import logging
log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    time_slot_size = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    slots = relationship("TimeSlot", backref='event',
            cascade='all, delete, delete-orphan')
    prelims = relationship("PrelimAssignment", backref='event',
            cascade='all, delete, delete-orphan')
    #meetings = relationship("Meeting", backref='event',
    #        cascade='all, delete, delete-orphan')

    def __repr__(self):
        try:
            return "<Event(id='%d', name='%s', time_slot_size='%d', active='%d')>" % (
                    self.id, self.name, self.time_slot_size, self.active)
        except TypeError:
            if self.id == None:
                log.debug("id field is None. Did you forget to flush?")
            raise

class TimeSlot(Base):
    __tablename__ = 'time_slots'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    time_slot = Column(DateTime, nullable=False)

    # These time slots indicate global busy times
    mark_global_busy = Column(Boolean, default=False)

    # True => marked busy
    # False => marked free
    # null => not marked
    mark_busy = Column(Boolean)

    # uniqname is populated if this is the result from a submitted user, it is
    # blank if this descibes the valid times for the event
    uniqname = Column(String(8))

    # The prelim_id maps back to a scheduled prelim. Note that the username
    # (must) also be populated for a scheduled prelim -- the effect is the add
    # to the set of times that are marked as busy for that user
    prelim_id = Column(Integer, ForeignKey("prelim_assignments.id"));

    def __repr__(self):
        return "<TimeSlot(id='{0}', event_id='{1}', time_slot='{2}' uniqname='{3}', prelim_id='{4}')>".format(
                self.id, self.event_id, self.time_slot, self.uniqname, self.prelim_id)

class Faculty(Base):
    __tablename__ = 'faculty'
    id = Column(Integer, primary_key=True)
    uniqname = Column(String(8), unique=True)
    name = Column(String(50))
    office = Column(String(50))
    enabled = Column(Boolean, default=True)

    def __repr__(self):
        return "<Faculty(id='{0}', uniqname='{1}', name='{2}', office='{3}')>".format(
                self.id, self.uniqname, self.name, self.office)

class PrelimAssignment(Base):
    __tablename__ = 'prelim_assignments'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    student_uniqname = Column(String(8), nullable=False)
    title = Column(Text)

    # Faculty 1-3 are the preferred faculty, faculty4 is the alternate
    faculty1 = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    faculty2 = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    faculty3 = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    faculty4 = Column(Integer, ForeignKey("faculty.id"), nullable=False)

    __table_args__ = (
            UniqueConstraint('event_id', 'student_uniqname'),
            CheckConstraint('faculty1 != faculty2'),
            CheckConstraint('faculty1 != faculty3'),
            CheckConstraint('faculty1 != faculty4'),
            CheckConstraint('faculty2 != faculty3'),
            CheckConstraint('faculty2 != faculty4'),
            CheckConstraint('faculty3 != faculty4'),
            )

    times = relationship("TimeSlot", backref='prelim',
            cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "<PrelimAssignment(id='{0}', event_id='{1}', student_uniqname='{2}', faculty1='{3}', faculty2='{4}', faculty3='{5}', faculty4='{6}')>".format(
                self.id, self.event_id, self.student_uniqname, self.faculty1, self.faculty2, self.faculty3, self.faculty4)

#class Meeting(Base):
#    __tablename__ = 'meetings'
#    id = Column(Integer, primary_key=True)
#    discriminator = Column('type', String(50))
#    __mapper_args__ = {'polymorphic_on': discriminator}
#
#    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
#
#    times = relationship("MeetingTimeSlot", backref='meeting',
#            cascade='all, delete, delete-orphan')
#
#class PrelimAssignment(Meeting):
#    __tablename__ = 'prelim_assignments'
#    __mapper_args__ = {'polymorphic_identity': 'prelim_assignment'}
#    id = Column(Integer, ForeignKey("meetings.id"), primary_key=True)
#
#    faculty_uniqname_1 = Column(String(8), ForeignKey("faculty.uniqname"))
#    faculty_uniqname_2 = Column(String(8), ForeignKey("faculty.uniqname"))
#    faculty_uniqname_3 = Column(String(8), ForeignKey("faculty.uniqname"))
#    student_uniqname = Column(String(8))
#
#class MeetingTimeSlot(Base):
#    __tablename__ = 'meeting_time_slots'
#    id = Column(Integer, primary_key=True)
#    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
#    datetime_slot = Column(DateTime, nullable=False)
#
#    def __repr__(self):
#        try:
#            return "<TimeSlot(id='%d', event_day_id='%d', uniqname='%s', time_slot='%s')>" % (
#                    self.id, self.event_day_id, self.uniqname, self.time_slot)
#        except TypeError:
#            if self.id == None:
#                log.debug("id field is None. Did you forget to flush?")
#            raise
