from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from source.database import Base
from dateutil import parser as DateParser
from source.database import db_session
import datetime

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    platform = Column(String(120))
    first_name = Column(String(120))
    last_name = Column(String(120))
    created = Column(DateTime)
    updated = Column(DateTime)

    device = relationship("Device", back_populates="contacts")

    def __repr__(self):
        return "<Contact(id='%d' device_id='%d' platform='%s' first_name='%s' last_name='%s' created='%s' updated='%s')" % \
               (self.id, self.device_id, self.platform, self.first_name, self.last_name, str(self.created), str(self.updated))

    def __init__(self, platform=None, first_name=None, last_name=None, created=datetime.datetime.now(), updated=datetime.datetime.now(), device=None):
        if platform is not None and platform != "":
            self.platform = platform
        if first_name is not None and first_name != "":
            self.first_name = first_name
        if last_name is not None and last_name != "":
            self.last_name = last_name
        if type(created) is str:
            self.created = DateParser.parse(created)
        else:
            self.created = created
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = updated
        if device is not None:
            self.device = device
            device.contacts.append(self)

    def updateContent(self, platform=None, first_name=None, last_name=None, created=None, updated=datetime.datetime.now(), device=None):
        if platform is not None and platform != "":
            self.platform = platform
        if first_name is not None and first_name != "":
            self.first_name = first_name
        if last_name is not None and last_name != "":
            self.last_name = last_name
        if type(created) is str:
            self.created = DateParser.parse(created)
        elif created is not None:
            self.created = created
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = updated
        if device is not None:
            self.device = device
            device.contacts.append(self)
        db_session.commit()

    def getNonSensitiveContent(self):
        return {"platform": self.platform,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "created": self.created,
                "updated": self.updated}
