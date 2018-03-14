from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from source.database import Base
from dateutil import parser as DateParser
from source.database import db_session
import datetime

class Message(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    message_text = Column(String(1024))
    platform = Column(String(120))
    time = Column(DateTime)

    # RELATIONS
    #user = relationship("User", back_populates="contact")

    #def __repr__(self):
    #    return "<Contact(id='%d' user_id='%d' platform='%s' first_name='%s' last_name='%s' created='%s' updated='%s')" % \
    #           (self.id, self.user_id, self.platform, self.first_name, self.last_name, str(self.created), str(self.updated))

    def __init__(self, platform=None, sender_id, receiver_id, message_text=None):
        self.platform = platform
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_text = message_text
        self.time = datetime.datetime.now()

