from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from dateutil import parser as DateParser
from config.database import db_session
import datetime

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    circle_id = Column(Integer, ForeignKey('circles.id'))
    name = Column(String(120))
    created = Column(DateTime)
    updated = Column(DateTime)

    # RELATIONS
    circle = relationship("Circle", back_populates="device")

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now(), name=None):
        if type(created) is str:
            self.created = DateParser.parse(created)
        else:
            self.created = datetime.datetime.now()
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = datetime.datetime.now()
        if name != None and name != "":
            self.name = name
        else:
            self.name = "My Device %d"%(self.id)

    def __repr__(self):
        return "<Device(id='%s' name='%s' created='%s' updated='%s')>" % (self.id, self.name, str(self.created), str(self.updated))

    def updateContent(self, created=None, updated=datetime.datetime.now(), name=None):
        if type(created) is str:
            self.created = DateParser.parse(created)
        elif created is not None:
            self.created = created
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        elif updated != None:
            self.updated = updated
        if name is not None and name != "":
            self.name = name
        db_session.commit()

    def getSimpleContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle_id": self.circle.id if self.circle is not None else -1
        }

    def getContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle": self.circle.getSimpleContent() if self.circle is not None else {}
        }
