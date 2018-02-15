from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from source.database import Base
from dateutil import parser as DateParser
import datetime

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    updated = Column(DateTime)

    # RELATIONS
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="devices")
    device_user = relationship("DeviceUser", back_populates="device")
    contacts = relationship("Contact", back_populates="device")

    def __init__(self, created=None, updated=None, user=None, device_user=None, contacts=None):
        if created is not None:
            self.created = DateParser.parse(created)
        else:
            self.created = datetime.datetime.now()
        if updated is not None:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = datetime.datetime.now()
        if user != None:
            self.user = user
        if device_user != None:
            self.device_user = device_user
        if contacts != None:
            self.contacts = contacts

    def __repr__(self):
        return "<Device(id='%s' created='%s' updated='%s')>" % (self.id, str(self.created), str(self.updated))

    def updateContent(self, created=None, updated=datetime.datetime.now(), user=None):
        if created is not None and created is not "":
            self.created = created
        if updated is not None and updated is not "":
            self.updated = updated
        if user is not None:
            self.user = user
            self.user.addresses.append(self)

    def getNonSensitiveContent(self):
        return {"created": self.created,
                "updated": self.updated}
