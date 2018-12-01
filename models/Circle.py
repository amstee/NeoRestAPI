from config.database import db
from dateutil import parser as DateParser
from flask_socketio import emit
import datetime
from utils.log import logger_set
from config.log import LOG_DATABASE_FILE
from mobile import push_android as android

logger = logger_set(module=__name__, file=LOG_DATABASE_FILE)


class Circle(db.Model):
    __tablename__ = "circles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    device = db.relationship("Device", uselist=False, back_populates="circle", cascade="all")
    user_link = db.relationship("UserToCircle", back_populates="circle", order_by="UserToCircle.id",
                                cascade="all, delete-orphan")
    circle_invite = db.relationship("CircleInvite", back_populates="circle", order_by="CircleInvite.id",
                                    cascade="all, delete-orphan")
    conversations = db.relationship("Conversation", back_populates="circle", order_by="Conversation.id",
                                    cascade="all, delete-orphan")
    media_links = db.relationship("CircleToMedia", back_populates="circle", order_by="CircleToMedia.id",
                                  cascade="all, delete-orphan")

    def __repr__(self):
        return "<Circle(id='%d' device_id='%d' users='%s')>" % (self.id, self.device.id, str(self.user_link))

    def __init__(self, name=None, created=datetime.datetime.now(), updated=datetime.datetime.now(), device=None):
        if name is not None and name != "":
            self.name = name
        if device is not None:
            self.device = device
            self.device.circle = self
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
        db.session.add(self)
        db.session.flush()
        logger.debug("Database add: circles%s", {"id": self.id,
                                                 "name": self.name,
                                                 "device": self.device.id if self.device is not None else -1})

    def has_member(self, member):
        for link in self.user_link:
            if link.user_id == member.id:
                return True
        return False

    def has_admin(self, member):
        for link in self.user_link:
            if link.user_id == member.id and link.privilege == "ADMIN":
                return True
        return False

    def has_invite(self, user):
        for invite in self.circle_invite:
            if invite.user_id == user.id:
                return True
        return False

    def check_validity(self):
        if len(self.user_link) == 0:
            db.session.delete(self)
            db.session.commit()

    def notify_users(self, p1='circle', p2=None):
        if p2 is None:
            p2 = {}
        p2['circle_id'] = self.id
        emit(p1, p2, room='circle_' + str(self.id), namespace='/')

    def notify_mobile(self, title, body, ignore=[]):
        for user_link in self.user_link:
            if user_link.user.id not in ignore:
                android.send_notification(user_link.user, title=title, body=body)

    def update_content(self, name=None, created=None, updated=datetime.datetime.now()):
        if name is not None and name != "":
            self.name = name
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
        db.session.commit()
        db.session.flush()
        logger.debug("Database update: circles%s", {"id": self.id,
                                                    "name": self.name,
                                                    "device": self.device.id if self.device is not None else -1})

    def remove_user(self, user):
        for user_link in self.user_link:
            if user_link.user_id == user.id:
                db.session.delete(user_link)
                db.session.commit()
                return True
        return False

    def get_simple_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "device": self.device.id if self.device is not None else -1,
        }

    def get_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "users": [link.get_content(False) for link in self.user_link],
            "device": self.device.get_simple_content() if self.device is not None else {},
            "invites": [invite.get_content(False) for invite in self.circle_invite],
            "conversations": [conv.get_simple_content() for conv in self.conversations],
            "medias": [link.get_content() for link in self.media_links]
        }
