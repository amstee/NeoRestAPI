from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base, db_session
from dateutil import parser as DateParser
import datetime

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    sent = Column(DateTime)
    read = Column(DateTime)
    text_content = Column(String(8192))
    link_id = Column(Integer, ForeignKey("user_to_conversation.id"))

    link = relationship("UserToConversation", back_populates="messages")
    medias = relationship("Media", back_populates="message", order_by="Message.id",
                              cascade="save-update, delete")

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
        db_session.commit()

    def getContent(self):
        return {
            "id": self.id,
            "link": self.link.getSimpleContent() if self.link is not None else {},
            "sent": self.sent,
            "read": self.read,
            "content": self.content,
            "medias": [media.getSimpleContent() for media in self.medias]
        }

    def getSimpleContent(self):
        return {
            "id": self.id,
            "link_id": self.link_id,
            "sent": self.sent,
            "read": self.read,
            "content": self.content
        }
