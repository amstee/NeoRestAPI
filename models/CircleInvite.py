from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from config.database import db_session
from dateutil import parser as DateParser
from config.sockets import sockets
import datetime


class CircleInvite(Base):
    __tablename__ = "circle_invites"
    id = Column(Integer, primary_key=True)
    circle_id = Column(Integer, ForeignKey("circles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created = Column(DateTime)
    updated = Column(DateTime)

    user = relationship("User", back_populates="circle_invite")
    circle = relationship("Circle", back_populates="circle_invite")

    def __repr__(self):
        return "<CircleInvite(id='%d' circle_id='%d' user_id='%d' created='%s' updated='%s')>" % (self.id,
                                                                                                  self.circle_id,
                                                                                                  self.user_id,
                                                                                                  str(self.created),
                                                                                                  str(self.updated))

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now()):
        if created is not None:
            if type(created) is str:
                self.created = DateParser.parse(created)
            else:
                self.created = created
        if updated is not None:
            if type(updated) is str:
                self.updated = DateParser.parse(updated)
            else:
                self.updated = updated
        db_session.add(self)

    def update_content(self, created=None, updated=datetime.datetime.now()):
        if created is not None:
            if type(created) is str:
                self.created = DateParser.parse(created)
            else:
                self.created = created
        if updated is not None:
            if type(updated) is str:
                self.updated = DateParser.parse(updated)
            else:
                self.updated = updated
        db_session.commit()

    def notify_user(self, p1='circle_invite', p2=None):
        if p2 is None:
            p2 = {}
        p2['circle_invite_id'] = self.id
        sockets.notify_user(self.user, False, p1, p2)

    def get_content(self, user=True):
        if user:
            return {
                "id": self.id,
                "updated": self.updated,
                "created": self.created,
                "user": self.user_id,
                "circle": self.circle.get_simple_content()
            }
        else:
            return {
                "id": self.id,
                "updated": self.updated,
                "created": self.created,
                "user": self.user.get_simple_content(),
                "circle": self.circle_id
            }
