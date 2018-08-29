from dateutil import parser as DateParser
from config.database import db
from utils.log import logger_set
import datetime

logger = logger_set(__name__)


class MessageToMedia(db.Model):
    __tablename__ = "message_to_media"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    media_id = db.Column(db.Integer, db.ForeignKey('medias.id'))
    upload_time = db.Column(db.DateTime)

    message = db.relationship("Message", back_populates="media_links")
    media = db.relationship("Media", back_populates="message_link")

    def __repr__(self):
        return "<MessageToMedia(id=%d, message_id=%d, media_id=%d)>" % (self.id, self.message_id, self.media_id)

    def __init__(self, message=None, media=None, upload_time=datetime.datetime.now()):
        if message is not None:
            self.message = message
        if media is not None:
            self.media = media
        if upload_time is not None:
            if type(upload_time) is str:
                self.upload_time = DateParser.parse(upload_time)
            else:
                self.upload_time = upload_time
        db.session.add(self)
        db.session.flush()
        logger.debug("Database add: message_to_media%s", {"id": self.id,
                                                          "message_id": self.message_id,
                                                          "media_id": self.media_id,})

    def update_content(self, message=None, media=None, upload_time=None):
        if message is not None:
            self.message = message
        if media is not None:
            self.media = media
        if upload_time is not None:
            if type(upload_time) is str:
                self.upload_time = DateParser.parse(upload_time)
            else:
                self.upload_time = upload_time
        db.session.commit()
        db.session.flush()
        logger.debug("Database update: message_to_media%s", {"id": self.id,
                                                             "message_id": self.message_id,
                                                             "media_id": self.media_id,})

    def get_content(self):
        return {
            "id": self.id,
            "message": self.message.get_simple_content(),
            "media": self.media.get_simple_content(),
            "upload_time": self.upload_time
        }

    def get_simple_content(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "media_id": self.media_id,
            "upload_time": self.upload_time
        }
