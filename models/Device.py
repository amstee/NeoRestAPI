from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from source.database import Base
from dateutil import parser as DateParser
from source.database import db_session
import datetime

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created = Column(DateTime)
    updated = Column(DateTime)

    # RELATIONS
    user = relationship("User", back_populates="devices")
    device_user = relationship("DeviceUser", back_populates="device")
    #contacts = relationship("Contact", back_populates="device")

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

    def updateContent(self, created=None, updated=datetime.datetime.now(), user=None,
                      device_user=None):
        if type(created) is str:
            self.created = DateParser.parse(created)
        elif created is not None:
            self.created = created
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = updated
        if user is not None:
            self.user = user
            self.user.devices.append(self)
        if device_user is not None:
            self.device_user = device_user
            self.device_user.device = self
        db_session.commit()

    def getNonSensitiveContent(self):
        return {
            "id": self.id,
            "created": self.created,
            "updated": self.updated}
