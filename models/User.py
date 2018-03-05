from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from source.database import Base
from source.database import db_session
from dateutil import parser as DateParser
import hashlib
import jwt
import datetime

SECRET_KEY = "defaultsecretkey"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(2048))
    first_name = Column(String(50))
    last_name = Column(String(50))
    birthday = Column(DateTime)
    searchText = Column(String(120))
    created = Column(DateTime)
    updated = Column(DateTime)
    jsonToken = Column(String(120))

    # RELATIONS
    device = relationship("Device", back_populates="user")
    contact = relationship("Contact", back_populates="user")

    def __init__(self, email=None, password=None, first_name=None, last_name=None,
                 birthday=None, searchText=None, created=datetime.datetime.now(),
                 updated=datetime.datetime.now()):
        user = db_session.query(User).filter_by(email=email).first()
        if user is not None:
            raise Exception("User already exist")
        if email is None or email == "" or password is None or password == "" or first_name is None \
                or last_name == "" or last_name is None or last_name == "" or birthday is None or birthday == "":
            raise Exception("Missing data to create a new user")
        self.email = email
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = DateParser.parse(birthday)
        if searchText is not None:
            self.searchText = searchText
        if created is not None:
            if type(created) is str:
                self.created = DateParser.parse(created)
            else:
                self.created = created
        if updated is not None:
            if type(updated) is str:
                self.updated = DateParser.parse(updated)
            else:
                self.updated = updated

    def __repr__(self):
        return '<User %r %r>' % (self.first_name, self.last_name)

    def disconnect(self):
        try:
            self.jsonToken = ""
            db_session.commit()
            return (True, None)
        except Exception as e:
            return (False, str(e))

    @staticmethod
    def decodeAuthToken(auth_token):
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            try:
                user = User.query.filter(User.id == payload['sub']).first()
                if user.jsonToken == "" or user.jsonToken == None:
                    return (False, 'User not authenticated, please login')
                return (True, user)
            except Exception as e:
                return (False, "An error occurred : " + str(e))
        except jwt.ExpiredSignatureError:
            return (False, 'Signature expired. Please log in again')
        except jwt.InvalidTokenError:
            return (False, 'Invalid token. Please log in again')

    def encodeAuthToken(self):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=1),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            self.jsonToken = token.decode()
            db_session.commit()
            return token.decode()
        except Exception as e:
            return (None)

    def Authenticate(self, password=None):
        if password != None and password != "":
            if self.password != hashlib.sha512(password.encode('utf-8')).hexdigest():
                return (False, "Wrong password")
            return (True, self.encodeAuthToken())
        return (False, "No password provided.")

    def updateContent(self, email=None, password=None, first_name=None, last_name=None, birthday=None,
                      searchText=None, created=None, updated=datetime.datetime.now()):
        if email is not None and email is not "":
            self.email = email
        if password is not None and password is not "":
            self.password = password
        if first_name is not None and first_name is not "":
            self.first_name = first_name
        if last_name is not None and last_name is not "":
            self.last_name = last_name
        if birthday is not None and birthday is not "" and type(birthday) is str:
            self.birthday = DateParser.parse(birthday)
        if searchText is not None and searchText is not "":
            self.searchText = searchText
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = updated
        if type(created) is str:
            self.created = DateParser.parse(created)
        elif created is not None:
            self.created = created
        db_session.commit()

    def getNonSensitiveContent(self):
        return {"id": self.id,
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "birthday": self.birthday,
                "searchText": self.searchText,
                "created": self.created,
                "updated": self.updated}
