from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from config.database import Base
from dateutil import parser as DateParser
from config.database import db_session
import datetime


class CircleToMedia(Base):
    __tablename__ = "circle_to_media"
    id = Column(Integer, primary_key=True)
    circle_id = Column(Integer, ForeignKey('circles.id'))
    media_id = Column(Integer, ForeignKey('medias.id'))
    upload_time = Column(DateTime)
    purpose = Column(String(16))

    circle = relationship("Circle", back_populates="media_links")
    media = relationship("Media", back_populates="circle_link")

    def __repr__(self):
        return "<CircleToMedia(id=%d, circle_id=%d, media_id=%d)>" % (self.id, self.circle_id, self.media_id)

    def __init__(self, circle=None, media=None, upload_time=datetime.datetime.now(), purpose="default"):
        if circle is not None:
            self.circle = circle
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

    def update_content(self, circle=None, media=None, upload_time=None, purpose=None):
        if circle is not None:
            self.circle = circle
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

    def get_content(self):
        return {
            "id": self.id,
            "circle": self.circle.get_simple_content(),
            "media": self.media.get_simple_content(),
            "upload_time": self.upload_time,
            "purpose": self.purpose
        }

    def get_simple_content(self):
        return {
            "id": self.id,
            "circle_id": self.circle_id,
            "media_id": self.media_id,
            "upload_time": self.upload_time,
            "purpose": self.purpose
        }
