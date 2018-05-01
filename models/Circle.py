from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from config.database import db_session
from models.UserToCircle import UserToCircle
from dateutil import parser as DateParser
import datetime

class Circle(Base):
    __tablename__ = "circles"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    created = Column(DateTime)
    updated = Column(DateTime)

    device = relationship("Device", uselist=False, back_populates="circle", cascade="save-update")
    userLink = relationship("UserToCircle", back_populates="circle", order_by="UserToCircle.id",
                            cascade="save-update, delete")
    circleInvites = relationship("CircleInvite", back_populates="circle", order_by="CircleInvite.id",
                                cascade="save-update, delete")
    conversations = relationship("Conversation", back_populates="circle", order_by="Conversation.id",
                                 cascade="save-update, delete")

    def __repr__(self):
        return "<Circle(id='%d' device_id='%d' users='%s')>"%(self.id, self.device.id, str(self.userLink))

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

    def hasMember(self, member):
        for link in self.userLink:
            if link.user_id == member.id:
                return True
        return False

    def updateContent(self, name=None, created=None, updated=datetime.datetime.now()):
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

    def addUser(self, user):
        link = UserToCircle()
        link.circle = self
        link.user = user
        self.userLink.append(link)
        user.circleLink.append(link)
        db_session.commit()

    def removeUser(self, user):
        for userlink in self.userLink:
            if userlink.user_id == user.id:
                db_session.remove(userlink)
                db_session.commit()
                return True
        return False

    def getSimpleContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "device": self.device.id if self.device is not None else -1,
        }

    def getContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "users": [link.getContent(False) for link in self.userLink],
            "device": self.device.getSimpleContent() if self.device is not None else {},
            "invites": [invite.getContent(False) for invite in self.circleInvites],
            "conversations": [conv.getSimpleContent() for conv in self.conversations]
        }