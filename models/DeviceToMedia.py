from dateutil import parser as DateParser
from config.database import db
from config.log import logger_set
import datetime

logger = logger_set(__name__)


class DeviceToMedia(db.Model):
    __tablename__ = "device_to_media"
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    media_id = db.Column(db.Integer, db.ForeignKey('medias.id'))
    upload_time = db.Column(db.DateTime)
    purpose = db.Column(db.String(16))

    device = db.relationship("Device", back_populates="media_links")
    media = db.relationship("Media", back_populates="device_link")
    
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
        db.session.add(self)
        db.session.flush()
        logger.debug("Database add: device_to_media%s", {"id": self.id,
                                                         "device_id": self.device_id,
                                                         "media_id": self.media_id,
                                                         "purpose": self.purpose})

    def update_content(self, device=None, media=None, upload_time=None, purpose=None):
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
        db.session.commit()
        db.session.flush()
        logger.debug("Database update: device_to_media%s", {"id": self.id,
                                                            "device_id": self.device_id,
                                                            "media_id": self.media_id,
                                                            "purpose": self.purpose})

    def get_content(self):
        return {
            "id": self.id,
            "device": self.device.get_simple_content(),
            "media": self.media.get_simple_content(),
            "upload_time": self.upload_time,
            "purpose": self.purpose
        }

    def get_simple_content(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "media_id": self.media_id,
            "upload_time": self.upload_time,
            "purpose": self.purpose
        }
