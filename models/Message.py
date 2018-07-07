from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config.database import Base, db_session
from dateutil import parser as DateParser
import datetime


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    link_id = Column(Integer, ForeignKey("user_to_conversation.id"), nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    sent = Column(DateTime)
    read = Column(DateTime)
    text_content = Column(String(8192))
    isUser = Column(Boolean)

    link = relationship("UserToConversation", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
    media_links = relationship("MessageToMedia", back_populates="message", order_by="MessageToMedia.id",
                               cascade="save-update, delete")
    device = relationship("Device", back_populates="messages")

    def __repr__(self):
        return "<NeoMessage(id='%d' sent='%s' read='%s')>"%(self.id, str(self.sent), str(self.read))

    def __init__(self, sent=datetime.datetime.now(), read=None, content=None, isUser=True,
                 link=None, conversation=None):
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
            self.text_content = content
        if link is not None:
            self.link = link
        if conversation is not None:
            self.conversation = conversation
        self.isUser = isUser
        db_session.add(self)

    def updateContent(self, sent=None, read=datetime.datetime.now(), content=None, isUser=None):
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
            self.text_content = content
        if isUser is not None:
            self.isUser = isUser
        db_session.commit()

    def getContent(self):
        if self.isUser:
            return {
                "id": self.id,
                "link": self.link.getSimpleContent() if self.link is not None else {},
                "sent": self.sent,
                "read": self.read,
                "content": self.text_content,
                "medias": [media.getContent() for media in self.media_links]
            }
        else:
            return {
                "id": self.id,
                "sent": self.sent,
                "read": self.read,
                "content": self.text_content,
                "medias": [media.getContent() for media in self.media_links],
                "device": self.device.getSimpleContent()
            }

    def getSimpleContent(self):
        if self.isUser:
            return {
                "id": self.id,
                "link_id": self.link_id,
                "sent": self.sent,
                "read": self.read,
                "content": self.text_content
            }
        else:
            return {
                "id": self.id,
                "device_id": self.device_id,
                "sent": self.sent,
                "read": self.read,
                "content": self.text_content
            }
