from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from source.database import Base

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    platform = Column(String(120), unique=True)
    first_name = Column(String(120), unique=True)
    last_name = Column(String(120), unique=True)
    created = Column(DateTime, unique=True)
    updated = Column(DateTime, unique=True)

    user = relationship("User", back_populates="contacts")

    def __repr__(self):
        return "<Contact(id='%d')" % (self.id)

    def updateContent(self, platform=None, first_name=None, last_name=None, created=None, updated=None, user=None):
        if platform is not None and platform != "":
            self.platform = platform
        if first_name is not None and first_name != "":
            self.first_name = first_name
        if last_name is not None and last_name != "":
            self.last_name = last_name
        if created is not None and created != "":
            self.created = created
        if updated is not None and updated != "":
            self.updated = updated

    def getNonSensitiveContent(self):
        return {"platform": self.platform,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "created": self.created,
                "updated": self.updated}
