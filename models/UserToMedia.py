from dateutil import parser as DateParser
from config.database import db
from config.log import logger_set
import datetime

logger = logger_set(__name__)


class UserToMedia(db.Model):
    __tablename__ = "user_to_media"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    media_id = db.Column(db.Integer, db.ForeignKey('medias.id'))
    upload_time = db.Column(db.DateTime)
    purpose = db.Column(db.String(16))

    user = db.relationship("User", back_populates="media_links")
    media = db.relationship("Media", back_populates="user_link")

    def __repr__(self):
        return "<UserToMedia(id=%d, user_id=%d, media_id=%d)>" % (self.id, self.user_id, self.media_id)

    def __init__(self, user=None, media=None, upload_time=datetime.datetime.now(), purpose="default"):
        if user is not None:
            self.user = user
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
        logger.debug("Database add: user_to_media%s", {"id": self.id,
                                                       "user_id": self.user_id,
                                                       "media_id": self.media_id,
                                                       "purpose": self.purpose})

    def update_content(self, user=None, media=None, upload_time=None, purpose=None):
        if user is not None:
            self.user = user
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
        logger.debug("Database update: user_to_media%s", {"id": self.id,
                                                          "user_id": self.user_id,
                                                          "media_id": self.media_id,
                                                          "purpose": self.purpose})

    def get_content(self):
        return {
            "id": self.id,
            "user": self.user.get_simple_content(),
            "media": self.media.get_simple_content(),
            "upload_time": self.upload_time,
            "purpose": self.purpose
        }

    def get_simple_content(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "media_id": self.media_id,
            "upload_time": self.upload_time,
            "purpose": self.purpose
        }
