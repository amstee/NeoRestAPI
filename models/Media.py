from sqlalchemy import Column, Integer, String, ForeignKey, event, Boolean
from sqlalchemy.orm import relationship
from config.database import Base
from config.database import db_session
from config.files import *
from werkzeug.utils import secure_filename
import os


class Media(Base):
    __tablename__ = "medias"
    id = Column(Integer, primary_key=True)
    filename = Column(String(120))
    extension = Column(String(10))
    directory = Column(String(1024))
    identifier = Column(String(10))

    message_link = relationship("MessageToMedia", back_populates="media", uselist=False,
                                cascade="save-update, delete")
    user_link = relationship("UserToMedia", back_populates="media", uselist=False,
                             cascade="save-update, delete")
    device_link = relationship("DeviceToMedia", back_populates="media", uselist=False,
                               cascade="save-update, delete")
    circle_link = relationship("CircleToMedia", back_populates="media", uselist=False,
                               cascade="save-update, delete")

    def __repr__(self):
        return "<Media(id='%d' filename='%s' extension='%s' directory='%s')>" % (
            self.id, self.filename, self.extension, self.directory
        )

    def upload(self, file):
        file_name = secure_filename(file.filename)
        if not os.path.exists(UPLOAD_FOLDER + self.directory + os.path.sep):
            os.makedirs(UPLOAD_FOLDER + self.directory + os.path.sep)
        file.save(os.path.join(UPLOAD_FOLDER + self.directory + os.path.sep, file_name))

    def clearFile(self):
        try:
            os.remove(os.path.join(UPLOAD_FOLDER + self.directory + os.path.sep, self.filename + self.extension))
            return True
        except Exception as e:
            return False

    def CanBeAccessedByDevice(self, device):
        if self.message_link is not None:
            if self.message_link.message.conversation.device_access is True:
                return self.message_link.message.conversation.circle_id == device.circle_id
        elif self.user_link is not None:
            return self.user_link.user.isInCircle(device.circle_id)
        elif self.device_link is not None:
            return self.device_link.device_id == device.id
        elif self.circle_link is not None:
            return self.circle_link.circle.device.id == device.id
        return False

    def CanBeAccessedByUser(self, user):
        if self.message_link is not None:
            return user.isInConversation(self.message_link.message.conversation_id)
        elif self.user_link is not None:
            if self.user_link.user_id == user.id:
                return True
            return user.hasMatchingCircle(self.user_link.user)
        elif self.device_link is not None:
            return user.isInCircle(self.device_link.device.circle_id)
        elif self.circle_link is not None:
            return self.circle_link.circle.hasAdmin(user)
        return False

    def CanBeUploadedByDevice(self, device):
        if self.message_link is not None:
            if self.message_link.message.isUser is False:
                if self.message_link.message.conversation.device_access is True:
                    return self.message_link.message.conversation.circle_id == device.circle_id
        elif self.user_link is not None:
            return False
        elif self.device_link is not None:
            return self.device_link.device_id == device.id
        elif self.circle_link is not None:
            return self.circle_link.circle.device.id == device.id
        return False

    def CanBeUploadedByUser(self, user):
        if self.message_link is not None:
            if self.message_link.message.isUser is True:
                return self.message_link.message.link.user_id == user.id
        elif self.user_link is not None:
            return self.user_link.user_id == user.id
        elif self.device_link is not None:
            return False
        elif self.circle_link is not None:
            return self.circle_link.circle.hasAdmin(user)
        return False

    def __init__(self, filename=None, extension=None, identifier=None, directory='default'):
        if filename is not None and filename != "":
            self.filename = filename
        if extension is not None and extension != "":
            self.extension = extension
        if identifier is not None and identifier != "":
            self.identifier = identifier
        self.directory = directory
        db_session.add(self)

    def setContent(self, file):
        file_name = secure_filename(file.filename)
        f, e = os.path.splitext(file_name)
        self.filename = f
        self.extension = e
        if self.message_link is not None:
            self.directory = "conversation_" + str(self.message_link.message.conversation_id)
        elif self.user_link is not None:
            self.directory = "user_" + str(self.user_link.user_id)
        elif self.circle_link is not None:
            self.directory = "circle_" + str(self.circle_link.circle_id)
        elif self.device_link is not None:
            self.directory = "device_" + str(self.device_link.device_id)
        else:
            raise Exception("Ce media est corrompu, vous ne pouvez pas upload de fichier")

    def getDirectory(self):
        return UPLOAD_FOLDER + self.directory + os.path.sep

    def getFullName(self):
        return self.filename + self.extension

    def updateContent(self, filename=None, extension=None, directory=None, identifier=None):
        if filename is not None and filename != "":
            self.filename = filename
        if extension is not None and extension != "":
            self.extension = extension
        if directory is not None and directory != "":
            self.directory = directory
        if identifier is not None and identifier != "":
            self.identifier = identifier
        db_session.commit()

    def getLinkType(self):
        if self.message_link is not None:
            return "conversation"
        elif self.user_link is not None:
            return "user"
        elif self.circle_link is not None:
            return "circle"
        elif self.device_link is not None:
            return "device"
        else:
            return "error"

    def getLinkContent(self):
        if self.message_link is not None:
            return self.message_link.getContent()
        elif self.user_link is not None:
            return self.user_link.getContent()
        elif self.circle_link is not None:
            return self.circle_link.getContent()
        elif self.device_link is not None:
            return self.device_link.getContent()
        else:
            return "error"

    def getContent(self):
        return {
            "id": self.id,
            "media_link": self.getLinkType(),
            "link_content": self.getLinkContent(),
            "filename": self.filename,
            "extension": self.extension,
            "directory": self.directory,
            "identifier": self.identifier
        }

    def getSimpleContent(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "extension": self.extension,
            "identifier": self.identifier
        }


@event.listens_for(Media, 'before_delete')
def receive_before_delete(mapper, connection, target):
    target.clearFile()
