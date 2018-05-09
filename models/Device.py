from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config.database import Base
from dateutil import parser as DateParser
from config.database import db_session
import random
import string
import jwt
import hashlib
import datetime
import base64

SECRET_KEY = "defaultdevicesecretkey"


class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    circle_id = Column(Integer, ForeignKey('circles.id'))
    key = Column(String(20))
    activated = Column(Boolean)
    username = Column(String(120), unique=True)
    password = Column(String(2048))
    jsonToken = Column(String(2048))
    name = Column(String(120))
    created = Column(DateTime)
    updated = Column(DateTime)

    # RELATIONS
    circle = relationship("Circle", back_populates="device")
    messages = relationship("Message", back_populates="device")

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now(),
                 username=None, name=None, activated=False):
        if type(created) is str:
            self.created = DateParser.parse(created)
        else:
            self.created = datetime.datetime.now()
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = datetime.datetime.now()
        if name != None and name != "":
            self.name = name
        else:
            self.name = "My Device %d"%(self.id)
        if activated is not None:
            self.activated = activated
        # USERNAME / PASSWORD AND KEY GENERATION
        # NEED TO INSTALL pycrypto and cypher the password for the storage before activation
        if username is not None:
            self.username = username
        else:
            c = True
            while c:
                username = ''.join(random.choice(string.ascii_uppercase) for _ in range(12))
                if db_session.query(Device).filter(Device.username==username).first() is None:
                    c = False
            self.username = username
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        self.password = base64.b64encode(str.encode(password)).decode('utf-8')
        self.key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
        db_session.add(self)

    def setPassword(self, password):
        self.password = base64.b64encode(str.encode(password)).decode('utf-8')

    def __repr__(self):
        return "<Device(id='%s' name='%s' created='%s' updated='%s')>" % (self.id, self.name, str(self.created), str(self.updated))

    def updateContent(self, created=None, updated=datetime.datetime.now(), name=None, activated=None):
        if type(created) is str:
            self.created = DateParser.parse(created)
        elif created is not None:
            self.created = created
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        elif updated != None:
            self.updated = updated
        if name is not None and name != "":
            self.name = name
        if activated is not None:
            self.activated = activated
        db_session.commit()

    def disconnect(self):
        self.jsonToken = ""
        db_session.commit()

    @staticmethod
    def decodeAuthToken(auth_token):
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            device = db_session.query(Device).filter(Device.id==payload['sub']).first()
            if device is not None:
                if device.jsonToken == "" or device.jsonToken is None:
                    return (False, "Device non authentifié")
                if device.activated == False:
                    return (False, "Device non activé")
                return (True, device)
            else:
                return (False, "Device Neo introuvable")
        except jwt.ExpiredSignatureError:
            return (False, "La session a expiré, authentifiez vous a nouveau")
        except jwt.InvalidTokenError:
            return (False, 'Token invalide, authentifiez vous a nouveau')
        except Exception as e:
            return (False, 'Une erreur est survenue : ' + str(e))

    def encodeAuthToken(self):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30, seconds=1),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            self.jsonToken = token.decode()
            db_session.commit()
            return token.decode()
        except Exception as e:
            print(e)
            return None

    def checkPassword(self, password=None):
        if password != None and password != "":
            if self.password == hashlib.sha512(password.encode("utf-8")).hexdigest():
                return True
        return False

    def Authenticate(self, password=None):
        if password != None and password != "":
            if self.password != hashlib.sha512(password.encode('utf-8')).hexdigest():
                return (False, "Mot de pass invalide")
            return (True, self.encodeAuthToken())
        return (False, "Aucun mot de passe fourni")

    def updatePassword(self, password=None):
        if password != None and password != "":
            self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
            db_session.commit()

    def activate(self, activation_key):
        if self.key == activation_key:
            self.activated = True
            pw = base64.b64decode(str.encode(self.password))
            self.password = hashlib.sha512(pw).hexdigest()
            db_session.commit()
        return self.activated

    def getPreActivationPassword(self):
        if self.activated is False:
            return base64.b64decode(str.encode(self.password)).decode('utf-8')
        raise Exception("Ce device est active")

    def getSimpleContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle_id": self.circle.id if self.circle is not None else -1,
            "activated": self.activated,
            "username": self.username
        }

    def getContent(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "activated": self.activated,
            "username": self.username,
            "circle": self.circle.getSimpleContent() if self.circle is not None else {},
            "messages" : [message.getSimpleContent() for message in self.messages]
        }
