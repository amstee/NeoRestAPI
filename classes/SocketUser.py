from flask_socketio import emit
from models.User import User
from models.Device import Device
from config.webrtc import EXPIRY, SECRET_KEY
from config.database import db
import time
import hashlib
import hmac


class SocketUser:
    sid = None
    connected = True
    authenticated = False
    token = None
    client_id = None
    is_device = False
    webrtc_username = ""
    webrtc_password = ""
    webrtc_credentials_valididity = 0

    def __init__(self, sid):
        self.sid = sid

    def __str__(self):
        return '<SocketClient(' + str(self.client_id) + ', ' + str(self.sid) + ')/>'

    @staticmethod
    def construct_client(client_id, is_device, data):
        if data is not None:
            client = SocketUser(data["sid"])
            client.client_id = client_id
            client.is_device = is_device
            client.connected = True if data["co"] == "True" else False
            client.authenticated = True if data["auth"] == "True" else False
            client.token = data["token"]
            client.webrtc_username = data["wu"]
            client.webrtc_password = data["wp"]
            client.webrtc_credentials_valididity = int(data["wcv"])
            return client
        return None

    def get_payload(self):
        return {"sid": self.sid, "co": self.connected, "auth": self.authenticated, "token": self.token,
                "wu": self.webrtc_username, "wp": self.webrtc_password,
                "wcv": self.webrtc_credentials_valididity}

    def get_key(self):
        if self.client_id is None:
            return None
        return ("d" if self.is_device else "u") + str(self.client_id)

    def generate_credentials(self):
        validity = time.time() + EXPIRY
        self.webrtc_username = str(validity) + ':' + str(self.client_id) + str(self.is_device)
        digest_maker = hmac.new(SECRET_KEY.encode('utf-8'), b'', hashlib.sha1)
        digest_maker.update(self.webrtc_username.encode('utf-8'))
        self.webrtc_password = digest_maker.digest()
        self.webrtc_credentials_valididity = validity
        return self.webrtc_username, self.webrtc_password

    def get_client(self):
        client = None
        if self.client_id is not None:
            if self.is_device:
                client = db.session.query(Device).filter(Device.id == self.client_id).first()
            else:
                client = db.session.query(User).filter(User.id == self.client_id).first()
        return client

    def authenticate(self, jwt_token):
        try:
            if self.authenticated is True:
                return False, "Already authenticated"
            b, client = User.decode_auth_token(jwt_token)
            if not b:
                b, client = Device.decode_auth_token(jwt_token)
                if b:
                    self.is_device = True
            if not b or client is None:
                return False, 'User not found'
            if client.json_token != jwt_token:
                return False, 'Invalid token'
            self.token = jwt_token
            self.client_id = client.id
            client.update_content(is_online=True)
            self.authenticated = True
            return True, 'User authenticated'
        except Exception as e:
            return False, str(e)

    def emit(self, event, data, namespace='/', room=None):
        if room is None:
            room = self.sid
        emit(event, data, room=room, namespace=namespace)

    def disconnect(self):
        if self.authenticated:
            client = self.get_client()
            if client is not None:
                client.update_content(is_online=False)

    def get_content(self):
        return {
            'sid': self.sid,
            'authenticated': self.authenticated,
            'client': self.client_id,
            'connected': self.connected,
            'is_device': self.is_device
        }
