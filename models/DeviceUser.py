from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from source.database import Base
from dateutil import parser as DateParser
import datetime

class DeviceUser(Base):
    __tablename__ = "device_users"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    first_name = Column(String(120))
    last_name = Column(String(120))
    birthday = Column(DateTime)
    created = Column(DateTime)
    updated = Column(DateTime)

    # RELATIONS
    device = relationship("Device", back_populates="devices")

    def __repr__(self):
        return "<DeviceUser(id='%s' first_name='%s' last_name='%s' birthday='%s' created='%s' updated='%s')>" % \
               (self.id, self.first_name, self.last_name, str(self.birthday), str(self.created), str(self.updated))

    def __init__(self, first_name=None, last_name=None, birthday=None, created=None, updated=None, device=None):
        self.first_name = first_name
        self.last_name = last_name
        if birthday is not None:
            self.birthday = DateParser.parse(birthday)
        else:
            self.birthday = datetime.datetime.now()
        if created is not None:
            self.created = DateParser.parse(created)
        else:
            self.created = datetime.datetime.now()
        if updated is not None:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = datetime.datetime.now()
        self.device = device


    def updateContent(self, first_name=None, last_name=None, birthday=None,
                      created=None, updated=datetime.datetime.now(), device=None):
        if first_name is not None and first_name is not "":
            self.first_name = first_name
        if last_name is not None and last_name is not "":
            self.last_name = last_name
        if birthday is not None:
            self.birthday = birthday
        if created is not None and created is not "":
            self.created = created
        if updated is not None and updated is not "":
            self.updated = updated
        if device is not None:
            self.device = device
            self.device.device_user = self

    def getNonSensitiveContent(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": self.birthday,
            "created": self.created,
            "updated": self.updated}
