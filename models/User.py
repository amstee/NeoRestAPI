from config.database import db
from dateutil import parser as DateParser
from utils.log import logger_set
import hashlib
import jwt
import datetime
from config.log import LOG_DATABASE_FILE
from config.facebook import SECRET_KEY as SECRET_KEY_BOT

logger = logger_set(module=__name__, file=LOG_DATABASE_FILE)
SECRET_KEY = ""


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(2048))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    birthday = db.Column(db.DateTime)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    json_token = db.Column(db.String(4096))
    facebook_psid = db.Column(db.String(256))
    hangout_space = db.Column(db.String(256))
    type = db.Column(db.String(10))
    is_online = db.Column(db.Boolean)

    # RELATIONS
    circle_link = db.relationship("UserToCircle", back_populates="user", order_by="UserToCircle.id",
                                  cascade="all, delete-orphan")
    conversation_links = db.relationship("UserToConversation", back_populates="user", order_by="UserToConversation.id",
                                         cascade="all, delete-orphan")
    circle_invite = db.relationship("CircleInvite", back_populates="user", order_by="CircleInvite.id",
                                    cascade="all, delete-orphan")
    media_links = db.relationship("UserToMedia", back_populates="user", order_by="UserToMedia.id",
                                  cascade="all, delete-orphan")

    def __init__(self, email=None, password=None, first_name=None, last_name=None,
                 birthday=None, is_online=False, created=datetime.datetime.now(),
                 updated=datetime.datetime.now()):
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None:
            raise Exception("L'utilisateur existe déja, réessayer avec une nouvelle adresse email")
        if email is None or email == "" or password is None or password == "" or first_name is None \
                or last_name == "" or last_name is None or last_name == "" or birthday is None or birthday == "":
            raise Exception("Données incomplete, impossible de créer l'utilisateur")
        self.email = email
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        self.first_name = first_name
        self.last_name = last_name
        try:
            if type(birthday) is str:
                self.birthday = DateParser.parse(birthday)
        except Exception:
            raise Exception("Date de naissance invalide")
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
        self.is_online = is_online
        self.type = "DEFAULT"
        self.facebook_psid = None
        self.hangout_space = None
        db.session.add(self)
        db.session.flush()
        logger.debug("Database add: users%s", self.get_simple_content())

    def __repr__(self):
        return '<User %r %r>' % (self.first_name, self.last_name)

    def disconnect(self):
        try:
            self.json_token = ""
            db.session.commit()
            return True, None
        except Exception as e:
            return False, str(e)

    def has_matching_circle(self, user):
        for link in self.circle_link:
            for link2 in user.circle_link:
                if link.circle_id == link2.circle_id:
                    return True
        return False

    def is_in_conversation(self, conversation_id):
        for link in self.conversation_links:
            if link.conversation_id == conversation_id:
                return True
        return False

    def is_in_circle(self, circle_id):
        for link in self.circle_link:
            if link.circle_id == circle_id:
                return True
        return False

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            try:
                user = db.session.query(User).filter(User.id == payload['sub']).first()
                if user is not None:
                    if user.json_token == "" or user.json_token is None:
                        return False, 'Utilisateur non authentifié'
                    return True, user
                else:
                    return False, 'Utilisateur introuvable'
            except Exception as e:
                return False, "Une erreur est survenue : " + str(e)
        except jwt.ExpiredSignatureError:
            return False, 'La session a expiré, authentifiez vous a nouveau'
        except jwt.InvalidTokenError:
            return False, 'Token invalide, authentifiez vous a nouveau'

    def notify_circles(self, p2):
        for link in self.circle_link:
            link.circle.notify_users(p2=p2)

    def encode_auth_token(self):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=1),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            self.json_token = token.decode()
            db.session.commit()
            return token.decode()
        except Exception as e:
            print(e)
            return None

    def encode_api_token(self):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=1),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id,
                'first_name': self.first_name,
                'last_name': self.last_name
            }
            token = jwt.encode(payload, SECRET_KEY_BOT, algorithm="HS256")
            return token.decode()
        except Exception as e:
            print(e)
            return None

    def check_password(self, password=None):
        if password is not None and password != "":
            if self.password != hashlib.sha512(password.encode("utf-8")).hexdigest():
                return False
            return True
        return False

    def authenticate(self, password=None):
        if password is not None and password != "":
            if self.password != hashlib.sha512(password.encode('utf-8')).hexdigest():
                return False, "Mot de passe invalide"
            try:
                if self.json_token is not None:
                    jwt.decode(self.json_token, SECRET_KEY)
                    return True, self.json_token
                return True, self.encode_auth_token()
            except jwt.ExpiredSignatureError:
                return True, self.encode_auth_token()
            except Exception:
                return True, self.encode_auth_token()
        return False, "Aucun mot de passe fourni"

    def update_password(self, password=None):
        if password is not None and password != "":
            self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
            db.session.commit()

    def update_content(self, email=None, first_name=None, last_name=None, birthday=None,
                       facebook_psid=None, hangout_space=None, is_online=None, created=None,
                       updated=datetime.datetime.now()):
        if email is not None and email is not "":
            self.email = email
        if first_name is not None and first_name is not "":
            self.first_name = first_name
        if last_name is not None and last_name is not "":
            self.last_name = last_name
        if birthday is not None and birthday is not "" and type(birthday) is str:
            self.birthday = DateParser.parse(birthday)
        if type(updated) is str:
            self.updated = DateParser.parse(updated)
        else:
            self.updated = updated
        if type(created) is str:
            self.created = DateParser.parse(created)
        elif created is not None:
            self.created = created
        if hangout_space is not None:
            self.hangout_space = hangout_space
        if facebook_psid is not None:
            self.facebook_psid = facebook_psid
        if is_online is not None:
            self.is_online = is_online
        db.session.commit()
        db.session.flush()
        logger.debug("Database update: users%s", self.get_simple_content())

    def promote_admin(self):
        self.type = "ADMIN"
        db.session.commit()

    @staticmethod
    def CreateNeoAdmin(password):
        admin = db.session.query(User).filter(User.email == "contact.projetneo@gmail.com").first()
        if admin is None:
            user = User(email="contact.projetneo@gmail.com", password=password,
                        first_name="Neo", last_name="Admin", birthday=datetime.datetime.now())
            user.promote_admin()

    def get_simple_content(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": self.birthday,
            "created": self.created,
            "updated": self.updated,
            "isOnline": self.is_online,
            "type": self.type,
        }

    def get_simple_json_compliant_content(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": None if self.birthday is None else self.birthday.isoformat(),
            "created": None if self.created is None else self.created.isoformat(),
            "updated": None if self.updated is None else self.updated.isoformat(),
            "isOnline": self.is_online,
            "type": self.type,
        }

    def get_content(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": self.birthday,
            "created": self.created,
            "updated": self.updated,
            "isOnline": self.is_online,
            "type": self.type,
            "hangout": False if self.hangout_space is None or len(self.hangout_space) == 0 else True,
            "facebook": False if self.facebook_psid is None or len(self.facebook_psid) == 0 else True,
            "circles": [link.get_content() for link in self.circle_link],
            "invites": [invite.get_content() for invite in self.circle_invite],
            "conversations": [link.get_simple_content() for link in self.conversation_links],
            "medias": [link.get_content() for link in self.media_links]
        }
