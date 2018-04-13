from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from dateutil import parser as DateParser
import datetime

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    sent = Column(DateTime)
    read = Column(DateTime)
    content = Column(String(8192))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    link = relationship("UserToConversation", back_populates="messages")

    def __repr__(self):
        return "<NeoMessage(id='%d' sent='%s' read='%s')>"%(self.id, str(self.sent), str(self.read))

    def __init__(self, sent=datetime.datetime.now(), read=None, content=None):
        if sent is not None:
            if type(sent) is str:
                self.sent = DateParser.parse(sent)
            else:
                self.sent = sent
        if read is not None:
            if type(read) is str:
                self.read = DateParser.parse(read)
            else:
                self.reed = read
        if content is not None:
            self.content = content

    def updateContent(self, sent=None, read=datetime.datetime.now(), content=None):
        if sent is not None:
            if type(sent) is str:
                self.sent = DateParser.parse(sent)
            else:
                self.sent = sent
        if read is not None:
            if type(read) is str:
                self.read = DateParser.parse(read)
            else:
                self.reed = read
        if content is not None:
            self.content = content

    def getContent(self):
        return {
            "id": self.id,
            "conv_link": self.link.getContent(),
            "user": self.user.getSimpleContent(),
            "sent": self.sent,
            "read": self.read,
            "content": self.content
        }

    def getSimpleContent(self):
        return {
            "id": self.id,
            "sent": self.sent,
            "read": self.read,
            "user": self.user_id,
            "content": self.content
        }
