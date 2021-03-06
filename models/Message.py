import datetime
from config.database import db
from dateutil import parser as DateParser
from utils.log import logger_set
from config.log import LOG_DATABASE_FILE

logger = logger_set(module=__name__, file=LOG_DATABASE_FILE)


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"))
    link_id = db.Column(db.Integer, db.ForeignKey("user_to_conversation.id"), nullable=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True)
    sent = db.Column(db.DateTime)
    read = db.Column(db.DateTime)
    text_content = db.Column(db.String(8192))
    is_user = db.Column(db.Boolean)

    link = db.relationship("UserToConversation", back_populates="messages")
    conversation = db.relationship("Conversation", back_populates="messages")
    media_links = db.relationship("MessageToMedia", back_populates="message", order_by="MessageToMedia.id",
                                  cascade="all, delete-orphan")
    device = db.relationship("Device", back_populates="messages")

    def __repr__(self):
        return "<NeoMessage(id='%d' sent='%s' read='%s')>" % (self.id, str(self.sent), str(self.read))

    def __init__(self, sent=datetime.datetime.now(), read=None, content=None, is_user=True,
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
        self.is_user = is_user
        db.session.add(self)
        db.session.flush()
        logger.debug("Database add: messages%s", self.get_simple_content())

    def update_content(self, sent=None, read=datetime.datetime.now(), content=None, is_user=None):
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
        if is_user is not None:
            self.is_user = is_user
        db.session.commit()
        db.session.flush()
        logger.debug("Database update: messages%s", self.get_simple_content())

    def get_content(self):
        if self.is_user:
            return {
                "id": self.id,
                "link": self.link.get_simple_content() if self.link is not None else {},
                "sent": self.sent,
                "read": self.read,
                "content": self.text_content,
                "medias": [media.get_content() for media in self.media_links]
            }
        else:
            return {
                "id": self.id,
                "sent": self.sent,
                "read": self.read,
                "content": self.text_content,
                "medias": [media.get_content() for media in self.media_links],
                "device": self.device.get_simple_content()
            }

    def get_simple_json_compliant_content(self):
        if self.is_user:
            return {
                "id": self.id,
                "link_id": self.link_id,
                "sent": None if self.sent is None else self.sent.isoformat(),
                "read": None if self.read is None else self.read.isoformat(),
                "content": self.text_content,
                "medias": len(self.media_links) if self.media_links is not None else 0
            }
        else:
            return {
                "id": self.id,
                "device_id": self.device_id,
                "sent": None if self.sent is None else self.sent.isoformat(),
                "read": None if self.read is None else self.read.isoformat(),
                "content": self.text_content,
                "medias": len(self.media_links) if self.media_links is not None else 0
            }

    def get_simple_content(self):
        if self.is_user:
            return {
                "id": self.id,
                "link_id": self.link_id,
                "sent": self.sent,
                "read": self.read,
                "content": self.text_content,
                "medias": len(self.media_links) if self.media_links is not None else 0
            }
        else:
            return {
                "id": self.id,
                "device_id": self.device_id,
                "sent": self.sent,
                "read": self.read,
                "content": self.text_content,
                "medias": len(self.media_links) if self.media_links is not None else 0
            }
