from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base, db_session
from dateutil import parser as DateParser
import datetime

class UserToConversation(Base):
    __tablename__ = "user_to_conversation"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    privilege = Column(String(10))
    created = Column(DateTime)
    updated = Column(DateTime)

    messages = relationship("Message", back_populates="link", order_by="Message.sent")
    conversation = relationship("Conversation", back_populates="links")
    user = relationship("User", back_populates="conversationLinks")

    def __repr__(self):
        return "<UserToConversation(id='%d' user_id='%d' conversation_id='%d' privilege='%s')>"%(
            self.id, self.user_id, self.conversation_id, self.privilege)

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now(),
                 privilege=None, user=None, conversation=None):
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
        if privilege is not None and privilege != "":
            self.privilege = privilege
        else:
            self.privilege = "STANDARD"
        if user is not None:
            self.user = user
        if conversation is not None:
            self.conversation = conversation
        db_session.add(self)

    def updateContent(self, created=None, updated=datetime.datetime.now(),
                 privilege=None):
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
        if privilege is not None and privilege != "":
            self.privilege = privilege
        db_session.commit()

    def getSimpleContent(self):
        return {
            "id": self.id,
            "created": self.created,
            "updated": self.updated,
            "privilege": self.privilege,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id
        }

    def getContent(self):
        return {
            "id": self.id,
            "created": self.created,
            "updated": self.updated,
            "privilege": self.privilege,
            "user_id": self.user.getSimpleContent(),
            "conversation_id": self.conversation.getSimpleContent(),
            "messages": [message.getSimpleContent() for message in self.messages]
        }

    def getMessages(self):
        return {
            "id": self.id,
            "messages": [message.getContent() for message in self.messages]
        }