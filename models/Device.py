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
    username = Column(String(128), unique=True)
    password = Column(String(2048))
    json_token = Column(String(2048))
    name = Column(String(128))
    created = Column(DateTime)
    updated = Column(DateTime)
    is_online = Column(Boolean)

    # RELATIONS
    circle = relationship("Circle", back_populates="device")
    messages = relationship("Message", back_populates="device")
    media_links = relationship("DeviceToMedia", back_populates="device", order_by="DeviceToMedia.id",
                               cascade="save-update, delete")

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now(),
                 username=None, name=None, activated=False, is_online=None):
        if type(created) is str:
            self.created = DateParser.parse(created)
        else:
            self.created = datetime.datetime.now()
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = datetime.datetime.now()
        if name is not None and name != "":
            self.name = name
        else:
            self.name = "My Device %d" % self.id
        if activated is not None:
            self.activated = activated
        if is_online is not None:
            self.is_online = is_online
        else:
            self.is_online = False
        # USERNAME / PASSWORD AND KEY GENERATION
        # NEED TO INSTALL pycrypto and cypher the password for the storage before activation
        if username is not None:
            self.username = username
        else:
            c = True
            while c:
                username = ''.join(random.choice(string.ascii_uppercase) for _ in range(12))
                if db_session.query(Device).filter(Device.username == username).first() is None:
                    c = False
            self.username = username
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        self.password = base64.b64encode(str.encode(password)).decode('utf-8')
        self.key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
        db_session.add(self)

    def set_password(self, password):
        self.password = base64.b64encode(str.encode(password)).decode('utf-8')

    def __repr__(self):
        return "<Device(id='%s' name='%s' created='%s' updated='%s')>" % \
               (self.id, self.name, str(self.created), str(self.updated))

    def update_content(self, created=None, updated=datetime.datetime.now(), name=None, activated=None, is_online=None):
        if type(created) is str:
            self.created = DateParser.parse(created)
        elif created is not None:
            self.created = created
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        elif updated is not None:
            self.updated = updated
        if name is not None and name != "":
            self.name = name
        if activated is not None:
            self.activated = activated
        if is_online is not None:
            self.is_online = is_online
        db_session.commit()

    def disconnect(self):
        self.json_token = ""
        db_session.commit()

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            device = db_session.query(Device).filter(Device.id == payload['sub']).first()
            if device is not None:
                if device.json_token == "" or device.json_token is None:
                    return False, "Device non authentifié"
                if not device.activated:
                    return False, "Device non activé"
                return True, device
            else:
                return False, "Device Neo introuvable"
        except jwt.ExpiredSignatureError:
            return False, "La session a expiré, authentifiez vous a nouveau"
        except jwt.InvalidTokenError:
            return False, 'Token invalide, authentifiez vous a nouveau'
        except Exception as e:
            return False, 'Une erreur est survenue : ' + str(e)

    def encode_auth_token(self):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30, seconds=1),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            self.json_token = token.decode()
            db_session.commit()
            return token.decode()
        except Exception as e:
            print(e)
            return None

    def check_password(self, password=None):
        if password is not None and password != "":
            if self.password == hashlib.sha512(password.encode("utf-8")).hexdigest():
                return True
        return False

    def authenticate(self, password=None):
        if password is not None and password != "":
            if self.password != hashlib.sha512(password.encode('utf-8')).hexdigest():
                return False, "Mot de pass invalide"
            try:
                if self.json_token is not None:
                    jwt.decode(self.json_token, SECRET_KEY)
                    return True, self.json_token
                return True, self.encode_auth_token()
            except jwt.ExpiredSignatureError:
                return True, self.encode_auth_token()
        return False, "Aucun mot de passe fourni"

    def update_password(self, password=None):
        if password is not None and password != "":
            self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
            db_session.commit()

    def activate(self, activation_key):
        if self.key == activation_key:
            self.activated = True
            pw = base64.b64decode(str.encode(self.password))
            self.password = hashlib.sha512(pw).hexdigest()
            db_session.commit()
        return self.activated

    def get_pre_activation_password(self):
        if self.activated is False:
            return base64.b64decode(str.encode(self.password)).decode('utf-8')
        raise Exception("Ce device est active")

    def get_simple_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "circle_id": self.circle.id if self.circle is not None else -1,
            "activated": self.activated,
            "username": self.username,
            "is_online": self.is_online
        }

    def get_simple_json_compliant_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": None if self.created is None else self.created.isoformat(),
            "updated": None if self.updated is None else self.updated.isoformat(),
            "circle_id": self.circle.id if self.circle is not None else -1,
            "activated": self.activated,
            "username": self.username,
            "is_online": self.is_online
        }

    def get_content(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "activated": self.activated,
            "username": self.username,
            "circle": self.circle.get_simple_content() if self.circle is not None else {},
            "messages": [message.get_simple_content() for message in self.messages],
            "medias": [link.get_content() for link in self.media_links],
            "is_online": self.is_online
        }
