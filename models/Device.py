from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from source.database import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created = Column(DateTime, unique=True)
    updated = Column(DateTime, unique=True)

    user = relationship("User", back_populates="devices")

    def __repr__(self):
        return "<Device(id='%s')>" % self.id

    def updateContent(self, created=None, updated=None, user=None):
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
