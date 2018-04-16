from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base, db_session
from dateutil import parser as DateParser
import datetime

class DeviceMessage(Base):
    __tablename__ = "device_messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    device_id = Column(Integer, ForeignKey('devices.id'))
    sent = Column(DateTime)
    read = Column(DateTime)
    text_content = Column(String(8192))

    medias = relationship("Media", back_populates="device_message", order_by="Media.id",
                          cascade="save-update, delete")
    user = relationship("User", back_populates="device_messages")
    device = relationship("Device", back_populates="messages")

    def __repr__(self):
        return "<DeviceMessage(id='%d', user_id='%d', sent='%s' read='%s' text_content='%s')>"%(
            self.id, self.user_id, str(self.sent), str(self.read), self.text_content
        )

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
            self.text_content = content

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
            self.text_content = content
        db_session.commit()

    def getContent(self):
        return {
            "id": self.id,
            "sent": self.sent,
            "read": self.read,
            "content": self.text_content,
            "medias": [media.getSimpleContent() for media in self.medias]
        }

    def getSimpleContent(self):
        return {
            "id": self.id,
            "sent": self.sent,
            "read": self.read,
            "content": self.text_content
        }