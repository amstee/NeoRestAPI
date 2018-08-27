from sqlalchemy import event
from config.database import db
from config.files import *
from werkzeug.utils import secure_filename
from config.log import logger_set
import os

logger = logger_set(__name__)


class Media(db.Model):
    __tablename__ = "medias"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120))
    extension = db.Column(db.String(10))
    directory = db.Column(db.String(1024))
    identifier = db.Column(db.String(10))
    uploaded = db.Boolean()

    message_link = db.relationship("MessageToMedia", back_populates="media", uselist=False,
                                   cascade="save-update, delete")
    user_link = db.relationship("UserToMedia", back_populates="media", uselist=False,
                                cascade="save-update, delete")
    device_link = db.relationship("DeviceToMedia", back_populates="media", uselist=False,
                                  cascade="save-update, delete")
    circle_link = db.relationship("CircleToMedia", back_populates="media", uselist=False,
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
        self.uploaded = True

    def clear_file(self):
        try:
            os.remove(os.path.join(UPLOAD_FOLDER + self.directory + os.path.sep, self.filename + self.extension))
            self.uploaded = False
            return True
        except Exception as e:
            return False

    def can_be_accessed_by_device(self, device):
        if self.message_link is not None:
            if self.message_link.message.conversation.device_access is True:
                return self.message_link.message.conversation.circle_id == device.circle_id
        elif self.user_link is not None:
            return self.user_link.user.is_in_circle(device.circle_id)
        elif self.device_link is not None:
            return self.device_link.device_id == device.id
        elif self.circle_link is not None:
            return self.circle_link.circle.device.id == device.id
        return False

    def can_be_accessed_by_user(self, user):
        if self.message_link is not None:
            return user.is_in_conversation(self.message_link.message.conversation_id)
        elif self.user_link is not None:
            if self.user_link.user_id == user.id:
                return True
            return user.has_matching_circle(self.user_link.user)
        elif self.device_link is not None:
            return user.is_in_circle(self.device_link.device.circle_id)
        elif self.circle_link is not None:
            return self.circle_link.circle.has_admin(user)
        return False

    def can_be_uploaded_by_device(self, device):
        if self.message_link is not None:
            if self.message_link.message.is_user is False:
                if self.message_link.message.conversation.device_access is True:
                    return self.message_link.message.conversation.circle_id == device.circle_id
        elif self.user_link is not None:
            return False
        elif self.device_link is not None:
            return self.device_link.device_id == device.id
        elif self.circle_link is not None:
            return self.circle_link.circle.device.id == device.id
        return False

    def can_be_uploaded_by_user(self, user):
        if self.message_link is not None:
            if self.message_link.message.is_user is True:
                return self.message_link.message.link.user_id == user.id
        elif self.user_link is not None:
            return self.user_link.user_id == user.id
        elif self.device_link is not None:
            return False
        elif self.circle_link is not None:
            return self.circle_link.circle.has_admin(user)
        return False

    def __init__(self, filename=None, extension=None, identifier=None, directory='default'):
        if filename is not None and filename != "":
            self.filename = filename
        if extension is not None and extension != "":
            self.extension = extension
        if identifier is not None and identifier != "":
            self.identifier = identifier
        self.directory = directory
        self.uploaded = False
        db.session.add(self)
        db.session.flush()
        logger.debug("Database add: medias%s", {"id": self.id,
                                                "filename": self.filename,
                                                "extension": self.extension,
                                                "identifier": self.identifier,
                                                "uploaded": self.uploaded})

    def set_content(self, file):
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

    def get_directory(self):
        return UPLOAD_FOLDER + self.directory + os.path.sep

    def get_full_name(self):
        return self.filename + self.extension

    def update_content(self, filename=None, extension=None, directory=None, identifier=None):
        if filename is not None and filename != "":
            self.filename = filename
        if extension is not None and extension != "":
            self.extension = extension
        if directory is not None and directory != "":
            self.directory = directory
        if identifier is not None and identifier != "":
            self.identifier = identifier
        db.session.commit()
        logger.debug("Database update: medias%s", {"id": self.id,
                                                   "filename": self.filename,
                                                   "extension": self.extension,
                                                   "identifier": self.identifier,
                                                   "uploaded": self.uploaded})

    def get_link_type(self):
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

    def get_link_content(self):
        if self.message_link is not None:
            return self.message_link.get_content()
        elif self.user_link is not None:
            return self.user_link.get_content()
        elif self.circle_link is not None:
            return self.circle_link.get_content()
        elif self.device_link is not None:
            return self.device_link.get_content()
        else:
            return "error"

    def get_content(self):
        return {
            "id": self.id,
            "media_link": self.get_link_type(),
            "link_content": self.get_link_content(),
            "filename": self.filename,
            "extension": self.extension,
            "directory": self.directory,
            "identifier": self.identifier,
            "uploaded": str(self.uploaded)
        }

    def get_simple_content(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "extension": self.extension,
            "identifier": self.identifier,
            "uploaded": str(self.uploaded)
        }


@event.listens_for(Media, 'before_delete')
def receive_before_delete(mapper, connection, target):
    target.clear_file()
