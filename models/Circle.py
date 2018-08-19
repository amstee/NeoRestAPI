from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from config.database import Base
from config.database import db_session
from dateutil import parser as DateParser
from flask_socketio import emit
import datetime


class Circle(Base):
    __tablename__ = "circles"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    created = Column(DateTime)
    updated = Column(DateTime)

    device = relationship("Device", uselist=False, back_populates="circle", cascade="save-update")
    user_link = relationship("UserToCircle", back_populates="circle", order_by="UserToCircle.id",
                             cascade="save-update, delete")
    circle_invite = relationship("CircleInvite", back_populates="circle", order_by="CircleInvite.id",
                                 cascade="save-update, delete")
    conversations = relationship("Conversation", back_populates="circle", order_by="Conversation.id",
                                 cascade="save-update, delete")
    media_links = relationship("CircleToMedia", back_populates="circle", order_by="CircleToMedia.id",
                               cascade="save-update, delete")

    def __repr__(self):
        return "<Circle(id='%d' device_id='%d' users='%s')>" % (self.id, self.device.id, str(self.user_link))

    def __init__(self, name=None, created=datetime.datetime.now(), updated=datetime.datetime.now(), device=None):
        if name is not None and name != "":
            self.name = name
        if device is not None:
            self.device = device
            self.device.circle = self
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

    def has_member(self, member):
        for link in self.user_link:
            if link.user_id == member.id:
                return True
        return False

    def has_admin(self, member):
        for link in self.user_link:
            if link.user_id == member.id and link.privilege == "ADMIN":
                return True
        return False

    def has_invite(self, user):
        for invite in self.circle_invite:
            if invite.user_id == user.id:
                return True
        return False

    def check_validity(self):
        if len(self.user_link) == 0:
            db_session.delete(self)
            db_session.commit()

    def notify_users(self, p1='circle', p2=None):
        if p2 is None:
            p2 = {}
        p2['circle_id'] = self.id
        emit(p1, p2, room='circle_' + str(self.id), namespace='/')

    def update_content(self, name=None, created=None, updated=datetime.datetime.now()):
        if name is not None and name != "":
            self.name = name
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

    def remove_user(self, user):
        for user_link in self.user_link:
            if user_link.user_id == user.id:
                db_session.delete(user_link)
                db_session.commit()
                return True
        return False

    def get_simple_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "device": self.device.id if self.device is not None else -1,
        }

    def get_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "users": [link.get_content(False) for link in self.user_link],
            "device": self.device.get_simple_content() if self.device is not None else {},
            "invites": [invite.get_content(False) for invite in self.circle_invite],
            "conversations": [conv.get_simple_content() for conv in self.conversations],
            "medias": [link.get_content() for link in self.media_links]
        }
