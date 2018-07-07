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

    def __repr__(self):
        return "<Media(id='%d' filename='%s' extension='%s' directory='%s')>"%(
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

    def __init__(self, filename=None, extension=None, identifier=None, directory='default'):
        if filename is not None and filename != "":
            self.filename = filename
        if extension is not None and extension != "":
            self.extension = extension
        if identifier is not None and identifier != "":
            self.identifier = identifier
        self.directory = directory
        db_session.add(self)

    def set_content(self, file, folder):
        file_name = secure_filename(file.filename)
        f, e = os.path.splitext(file_name)
        self.filename = f
        self.extension = e
        self.directory = folder

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

    def getContent(self):
        if self.message_link is not None:
            return {
                "id": self.id,
                "message": self.message_link.getContent(),
                "filename": self.filename,
                "extension": self.extension,
                "directory": self.directory,
                "identifier": self.identifier
            }
        else:
            return {
                "id": self.id,
                "message": "None",
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
