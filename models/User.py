from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from config.database import Base
from config.database import db_session
from dateutil import parser as DateParser
import hashlib
import jwt
import datetime

SECRET_KEY = "defaultusersecretkey"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(2048))
    first_name = Column(String(50))
    last_name = Column(String(50))
    birthday = Column(DateTime)
    created = Column(DateTime)
    updated = Column(DateTime)
    jsonToken = Column(String(4096))
    facebookPSID = Column(BigInteger)
    type = Column(String(10))

    # RELATIONS
    circleLink = relationship("UserToCircle", back_populates="user", order_by="UserToCircle.id",
                              cascade="save-update, delete")
    conversationLinks = relationship("UserToConversation", back_populates="user", order_by="UserToConversation.id",
                                     cascade="save-update, delete")
    circleInvite = relationship("CircleInvite", back_populates="user", order_by="CircleInvite.id", cascade="save-update, delete")

    def __init__(self, email=None, password=None, first_name=None, last_name=None,
                 birthday=None, created=datetime.datetime.now(),
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
        if type(birthday) is str:
            self.birthday = DateParser.parse(birthday)
        else:
            self.birthday = birthday
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
        self.type = "DEFAULT"
        self.facebookPSID = -1
        db_session.add(self)

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
                user = db_session.query(User).filter(User.id == payload['sub']).first()
                if user is not None:
                    if user.jsonToken == "" or user.jsonToken == None:
                        return (False, 'Utilisateur non authentifié')
                    return (True, user)
                else:
                    return (False, 'Utilisateur introuvable')
            except Exception as e:
                return (False, "Une erreur est survenue : " + str(e))
        except jwt.ExpiredSignatureError:
            return (False, 'La session a expiré, authentifiez vous a nouveau')
        except jwt.InvalidTokenError:
            return (False, 'Token invalide, authentifiez vous a nouveau')

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
            print(e)
            return (None)

    def encodeApiToken(self):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=1),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id,
                'first_name': self.first_name,
                'last_name': self.last_name
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return token.decode()
        except Exception as e:
            print(e)
            return (None)

    def checkPassword(self, password=None):
        if password != None and password != "":
            if self.password != hashlib.sha512(password.encode("utf-8")).hexdigest():
                return False
            return True
        return False


    def Authenticate(self, password=None):
        if password != None and password != "":
            if self.password != hashlib.sha512(password.encode('utf-8')).hexdigest():
                return (False, "Mot de passe invalide")
            return (True, self.encodeAuthToken())
        return (False, "Aucun mot de passe fourni")

    def updatePassword(self, password=None):
        if password != None and password != "":
            self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
            db_session.commit()

    def updateContent(self, email=None, first_name=None, last_name=None, birthday=None,
                      searchText=None, facebookPSID=None, created=None, updated=datetime.datetime.now()):
        if email is not None and email is not "":
            self.email = email
        if first_name is not None and first_name is not "":
            self.first_name = first_name
        if last_name is not None and last_name is not "":
            self.last_name = last_name
        if birthday is not None and birthday is not "" and type(birthday) is str:
            self.birthday = DateParser.parse(birthdsay)
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
        self.facebookPSID = facebookPSID
        db_session.commit()

    def promoteAdmin(self):
        self.type = "ADMIN"
        db_session.commit()

    @staticmethod
    def CreateNeoAdmin():
        admin = db_session.query(User).filter(User.email=="contact.projetneo@gmail.com").first()
        if admin is None:
            user = User(email="contact.projetneo@gmail.com", password="PapieNeo2019",
                        first_name="Neo", last_name="Admin", birthday=datetime.datetime.now())
            user.promoteAdmin()

    def getSimpleContent(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": self.birthday,
            "created": self.created,
            "updated": self.updated,
            "type": self.type,
        }

    def getContent(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": self.birthday,
            "created": self.created,
            "updated": self.updated,
            "type": self.type,
            "circles": [link.getContent() for link in self.circleLink],
            "invites": [invite.getContent() for invite in self.circleInvite],
            "conversations": [link.getSimpleContent() for link in self.conversationLinks]
        }
