from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from config.database import Base
from dateutil import parser as DateParser
from config.database import db_session
import datetime


class DeviceToMedia(Base):
    __tablename__ = "device_to_media"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    media_id = Column(Integer, ForeignKey('medias.id'))
    upload_time = Column(DateTime)
    purpose = Column(String(16))

    device = relationship("Device", back_populates="media_links")
    media = relationship("Media", back_populates="device_link")
    
    def __repr__(self):
        return "<DeviceToMedia(id=%d, device_id=%d, media_id=%d)>" % (self.id, self.device_id, self.media_id)

    def __init__(self, device=None, media=None, upload_time=datetime.datetime.now(), purpose="default"):
        if device is not None:
            self.device = device
        if media is not None:
            self.media = media
        if upload_time is not None:
            if type(upload_time) is str:
                self.upload_time = DateParser.parse(upload_time)
            else:
                self.upload_time = upload_time
        if purpose is not None:
            self.purpose = purpose
        db_session.add(self)

    def updateContent(self, device=None, media=None, upload_time=None, purpose=None):
        if device is not None:
            self.device = device
        if media is not None:
            self.media = media
        if upload_time is not None:
            if type(upload_time) is str:
                self.upload_time = DateParser.parse(upload_time)
            else:
                self.upload_time = upload_time
        if purpose is not None:
            self.purpose = purpose
        db_session.commit()

    def getContent(self):
        return {
            "id": self.id,
            "device": self.device.getSimpleContent(),
            "media": self.media.getSimpleContent(),
            "upload_time": self.upload_time,
            "purpose": self.purpose
        }

    def getSimpleContent(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "media_id": self.media_id,
            "upload_time": self.upload_time,
            "purpose": self.purpose
        }
