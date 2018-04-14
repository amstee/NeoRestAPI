from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base, db_session
from dateutil import parser as DateParser
import datetime

class UserToCircle(Base):
    __tablename__ = "user_to_circle"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    circle_id = Column(Integer, ForeignKey("circles.id"))
    created = Column(DateTime)
    updated = Column(DateTime)
    privilege = Column(String(10))

    user = relationship("User", back_populates="circleLink")
    circle = relationship("Circle", back_populates="userLink")

    def __repr__(self):
        return "<UserToCircle(id='%d' user_id='%d' circle_id='%d' created='%s' updated='%s' privilege='%s')>"%(self.id, self.user_id, self.circle_id, str(self.created), str(self.updated), self.privilege)

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now(), privilege=None,
                 user=None, circle=None):
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
        if privilege is not None:
            self.privilege = privilege
        if user is not None:
            self.user = user
        if circle is not None:
            self.circle = circle

    def updateContent(self, created=None, updated=datetime.datetime.now(), privilege=None):
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
        db_session.commit()

    def getContent(self, user=True):
        if user:
            return {
                "id": self.id,
                "user": self.user_id,
                "circle": self.circle.getSimpleContent(),
                "created": self.created,
                "updated": self.updated,
                "privilege": self.privilege
            }
        else:
            return {
                "id": self.id,
                "user": self.user.getSimpleContent(),
                "circle": self.circle_id,
                "created": self.created,
                "updated": self.updated,
                "privilege": self.privilege
            }
