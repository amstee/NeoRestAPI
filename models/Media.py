from sqlalchemy import Column, Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship
from config.database import Base
from config.database import db_session
from werkzeug.utils import secure_filename
import os


class Media(Base):
    __tablename__ = "medias"
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'))
    filename = Column(String(120))
    extension = Column(String(10))
    directory = Column(String(1024))

    message = relationship("Message", back_populates="medias")

    def __repr__(self):
        return "<Media(id='%d' message_id='%d' filename='%s' extension='%s' directory='%s')>"%(
            self.id, self.message_id, self.filename, self.extension, self.directory
        )

    def upload(self, file):
        file_name = secure_filename(file.filename)
        file.save(os.path.join(self.directory, file_name))

    def clearFile(self):
        try:
            os.remove(os.path.join(self.directory, self.filename + self.extension))
            return True
        except Exception as e:
            return False

    def __init__(self, filename=None, extension=None, directory="/Users/Neo/Media/"):
        if filename is not None and filename != "":
            self.filename = filename
        if extension is not None and extension != "":
            self.extension = extension
        self.directory = directory

    def setContent(self, file=None, directory="default", message=None):
        if file is not None:
            name, ext = os.path.splitext(secure_filename(file.filename))
            directory = "/Users/Neo/Media/" + directory + "/"
            self.filename = name
            self.extension = ext
            self.directory = directory
            if message is not None:
                self.message = message
            self.upload(file)
        return self

    def updateContent(self, filename=None, extension=None, directory=None):
        if filename is not None and filename != "":
            self.filename = filename
        if extension is not None and extension != "":
            self.extension = extension
        if directory is not None and directory != "":
            self.directory = directory
        db_session.commit()

    def getContent(self):
        return {
            "id": self.id,
            "message": self.message.getSimpleContent(),
            "filename": self.filename,
            "extension": self.extension,
            "directory": self.directory
        }

    def getSimpleContent(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "filename": self.filename,
            "extension": self.extension
        }

@event.listens_for(Media, 'before_delete')
def receive_before_delete(target):
    target.clearFile()
