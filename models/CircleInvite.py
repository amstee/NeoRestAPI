from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from config.database import db_session
from models.UserToCircle import UserToCircle
from dateutil import parser as DateParser
import datetime

class CircleInvite(Base):
    __tablename__ = "circle_invites"
    id = Column(Integer, primary_key=True)
    circle_id = Column(Integer, ForeignKey("circles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created = Column(DateTime)
    updated = Column(DateTime)

    circle = relationship("Circle", back_populates="circleInvites")
    user = relationship("User", back_populates="circleInvites")

    def __repr__(self):
        return "<CircleInvite(id='%d' circle_id='%d' user_id='%d' created='%s' updated='%s')>"%(self.id, self.circle_id, self.user_id, str(self.created), str(self.updated))

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now()):
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

    def updateContent(self, created=None, updated=datetime.datetime.now()):
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
        db_session.commit()

    def getContent(self, user=True):
        if user:
            return {
                "id": self.id,
                "updated": self.updated,
                "created": self.created,
                "user": self.user_id,
                "circle": self.circle.getSimpleContent()
            }
        else:
            return {
                "id": self.id,
                "updated": self.updated,
                "created": self.created,
                "user": self.user.getSimpleContent(),
                "circle": self.circle_id
            }