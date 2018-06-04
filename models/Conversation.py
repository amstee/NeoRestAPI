from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config.database import Base, db_session
from dateutil import parser as DateParser
from config.sockets import sockets
import datetime

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    circle_id = Column(Integer, ForeignKey("circles.id"))
    name = Column(String(120))
    created = Column(DateTime)
    updated = Column(DateTime)
    device_access = Column(Boolean)

    circle = relationship("Circle", back_populates="conversations")
    links = relationship("UserToConversation", back_populates="conversation")
    messages = relationship("Message", back_populates="conversation", order_by="Message.id",
                            cascade="save-update, delete")

    def __repr__(self):
        return "<Conversation(id='%d' name='%s' created='%s' updated='%s')>"%(self.id, self.name, str(self.created), str(self.updated))

    def __init__(self, name=None, created=datetime.datetime.now(), updated=datetime.datetime.now(),
                 device_access=False, circle=None):
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
        if name is not None and name != "":
            self.name = name
        else:
            self.name = "Conversation"
        if circle is not None:
            self.circle = circle
        self.device_access = device_access
        db_session.add(self)

    def hasMembers(self, *args):
        for member in args:
            tf = False
            for link in self.links:
                if link.user_id == member.id:
                    tf = True
            if tf is False:
                return False
        return True

    def updateContent(self, created=None, updated=datetime.datetime.now(), name=None, device_access=None):
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
        if name is not None and name != "":
            self.name = name
        if device_access is not None:
            self.device_access = device_access
        db_session.commit()

    def notify_users(self, p1='Conversation', p2='modify'):
        for link in self.links:
            sockets.notify_user(link.user, p1, p2)

    def setOtherAdmin(self):
        for link in self.links:
            link.updateContent(privilege="ADMIN")
            return True

    def checkValidity(self):
        if (len(self.links) + (1 if self.device_access else 0)) <= 1:
            for link in self.links:
                db_session.delete(link)
            db_session.delete(self)
            return False
        return True

    def getContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle": self.circle.getSimpleContent(),
            "links": [link.getContent() for link in self.links],
            "messages": [message.getSimpleContent() for message in self.messages],
            "device_access": self.device_access
        }

    def getSimpleContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle_id": self.circle_id,
            "device_access": self.device_access
        }