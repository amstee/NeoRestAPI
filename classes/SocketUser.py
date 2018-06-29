from flask_socketio import emit
from models.User import User
from models.Device import Device


class SocketUser:
    sid = None
    connected = True
    authenticated = False
    token = None
    client = None
    is_device = False

    def __init__(self, sid):
        self.sid = sid

    def __str__(self):
        return '<SocketUser(' + str(self.sid) + " Connected : " + \
               str(self.connected) + " Authenticated : " + str(self.authenticated) + ')>'

    def authenticate(self, jwt_token):
        try:
            b, client = User.decodeAuthToken(jwt_token)
            if not b:
                b, client = Device.decodeAuthToken(jwt_token)
                if b:
                    self.is_device = True
            if not b or client is None:
                return False, 'User not found'
            if client.jsonToken != jwt_token:
                return False, 'Invalid token'
            self.token = jwt_token
            self.client = client
            self.client.updateContent(is_online=True)
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
            self.client.updateContent(is_online=False)

    def getContent(self):
        return {
            'sid': self.sid,
            'authenticated': self.authenticated,
            'client': self.client.getSimpleContent(),
            'connected': self.connected,
            'is_device': self.is_device
        }