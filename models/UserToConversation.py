from config.database import db
from dateutil import parser as DateParser
import datetime


class UserToConversation(db.Model):
    __tablename__ = "user_to_conversation"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"))
    privilege = db.Column(db.String(10))
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    messages = db.relationship("Message", back_populates="link", order_by="Message.sent")
    conversation = db.relationship("Conversation", back_populates="links")
    user = db.relationship("User", back_populates="conversation_links")

    def __repr__(self):
        return "<UserToConversation(id='%d' user_id='%d' conversation_id='%d' privilege='%s')>" % (
            self.id, self.user_id, self.conversation_id, self.privilege)

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now(),
                 privilege=None, user=None, conversation=None):
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
        if privilege is not None and privilege != "":
            self.privilege = privilege
        else:
            self.privilege = "STANDARD"
        if user is not None:
            self.user = user
        if conversation is not None:
            self.conversation = conversation
        db.session.add(self)

    def update_content(self, created=None, updated=datetime.datetime.now(),
                       privilege=None):
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
        if privilege is not None and privilege != "":
            self.privilege = privilege
        db.session.commit()

    def get_simple_content(self):
        return {
            "id": self.id,
            "created": self.created,
            "updated": self.updated,
            "privilege": self.privilege,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "circle_id": self.conversation.circle_id
        }

    def get_content(self):
        return {
            "id": self.id,
            "created": self.created,
            "updated": self.updated,
            "privilege": self.privilege,
            "user_id": self.user.get_simple_content(),
            "conversation_id": self.conversation.get_simple_content(),
            "circle_id": self.conversation.circle_id,
            "messages": [message.get_simple_content() for message in self.messages]
        }

    def get_messages(self):
        return {
            "id": self.id,
            "messages": [message.get_content() for message in self.messages]
        }
