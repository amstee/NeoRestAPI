from flask_socketio import emit, join_room
from models.User import User, SECRET_KEY
from config.database import db_session
import jwt


class SocketUser:
    sid = None
    connected = True
    authenticated = False
    token = None
    user = None

    def __init__(self, sid):
        self.sid = sid

    def __str__(self):
        return '<SocketUser(' + str(self.sid) + " Connected : " + \
               str(self.connected) + " Authenticated : " + str(self.authenticated) + ')>'

    def authenticate(self, jwt_token):
        try:
            token = jwt.decode(jwt_token, SECRET_KEY)
            user = db_session.query(User).filter(User.id == token['sub']).first()
            if user is None:
                return False, 'User not found'
            if user.jsonToken != jwt_token:
                return False, 'Invalid token'
            self.token = jwt_token
            self.user = user
            self.user.updateContent(is_online=True)
            self.authenticated = True
            return True, self.user
        except Exception as e:
            return False, str(e)

    def emit(self, event, data, room=sid):
        emit(event, data, room=room, namespace='/')

    def disconnect(self):
        if self.authenticated:
            self.user.updateContent(is_online=False)

    def getContent(self):
        return {
            'sid': self.sid,
            'authenticated': self.authenticated,
            'user': self.user.getSimpleContent(),
            'connected': self.connected
        }