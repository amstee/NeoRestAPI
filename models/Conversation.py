from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base, db_session
from dateutil import parser as DateParser
import datetime

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    circle_id = Column(Integer, ForeignKey("circles.id"))
    name = Column(String(120))
    created = Column(DateTime)
    updated = Column(DateTime)

    circle = relationship("Circle", back_populates="conversations")
    links = relationship("UserToConversation", back_populates="conversation")

    def __repr__(self):
        return "<Conversation(id='%d' name='%s' created='%s' updated='%s')>"%(self.id, self.name, str(self.created), str(self.updated))

    def __init__(self, name=None, created=datetime.datetime.now(), updated=datetime.datetime.now()):
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
            self.name = "Conversation %d"%self.id

    def updateContent(self, created=None, updated=datetime.datetime.now(), name=None):
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
        db_session.commit()

    def getContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle": self.circle.getSimpleContent(),
            "links": [link.getContent() for link in self.links]
        }

    def getSimpleContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle_id": self.circle_id
        }