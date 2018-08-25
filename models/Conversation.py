from config.database import db
from dateutil import parser as DateParser
from flask_socketio import emit
from config.log import logger_set
import datetime

logger = logger_set(__name__)


class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    circle_id = db.Column(db.Integer, db.ForeignKey("circles.id"))
    name = db.Column(db.String(120))
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    device_access = db.Column(db.Boolean)

    circle = db.relationship("Circle", back_populates="conversations")
    links = db.relationship("UserToConversation", back_populates="conversation")
    messages = db.relationship("Message", back_populates="conversation", order_by="Message.id",
                               cascade="save-update, delete")

    def __repr__(self):
        return "<Conversation(id='%d' name='%s' created='%s' updated='%s')>" % (self.id, self.name,
                                                                                str(self.created), str(self.updated))

    def __init__(self, name=None, created=datetime.datetime.now(), updated=datetime.datetime.now(),
                 device_access=False, circle=None):
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
        if name is not None and name != "":
            self.name = name
        else:
            self.name = "Conversation"
        if circle is not None:
            self.circle = circle
        self.device_access = device_access
        db.session.add(self)
        db.session.flush()
        logger.debug("Database add: conversations%s", {"id": self.id,
                                                       "name": self.name,
                                                       "circle_id": self.circle_id,
                                                       "device_access": self.device_access})

    def has_members(self, *args):
        for member in args:
            tf = False
            for link in self.links:
                if link.user_id == member.id:
                    tf = True
            if tf is False:
                return False
        return True

    def update_content(self, created=None, updated=datetime.datetime.now(), name=None, device_access=None):
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
        if name is not None and name != "":
            self.name = name
        if device_access is not None:
            self.device_access = device_access
        db.session.commit()
        db.session.flush()
        logger.debug("Database update: conversations%s", {"id": self.id,
                                                          "name": self.name,
                                                          "circle_id": self.circle_id,
                                                          "device_access": self.device_access})

    def notify_users(self, p1='conversation', p2=None):
        if p2 is None:
            p2 = {}
        p2['conversation_id'] = self.id
        emit(p1, p2, room='conversation_' + str(self.id), namespace='/')

    def set_other_admin(self):
        for link in self.links:
            link.update_content(privilege="ADMIN")
            return True

    def check_validity(self):
        if (len(self.links) + (1 if self.device_access else 0)) <= 1:
            for link in self.links:
                db.session.delete(link)
            db.session.delete(self)
            return False
        return True

    def get_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle": self.circle.get_simple_content(),
            "links": [link.get_content() for link in self.links],
            "messages": [message.get_simple_content() for message in self.messages],
            "device_access": self.device_access
        }

    def get_simple_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle_id": self.circle_id,
            "device_access": self.device_access
        }
