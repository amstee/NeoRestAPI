import unittest
import sys
from flask_socketio import SocketIOTestClient
sys.path.insert(0, '..')
from api import neoapi
from config.database import db_session
from utils.testutils import AuthenticateUser
from models.User import User as UserModel


class SocketioAuthenticate(unittest.TestCase):
    def setUp(self):
        self.neo = neoapi()
        self.api = self.neo.activate_testing()
        self.client = SocketIOTestClient(self.neo.app, self.neo.socketio)
        self.client.disconnect()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "te@test.com").first()
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "user1.beta@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="te@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")

    def tearDown(self):
        self.client.disconnect()

    def test_invalid_join_conversation(self):
        data = {
            'token': self.token1
        }
        assert len(self.neo.sockets) == 0
        self.client.connect()
        self.client.emit('authenticate', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        data = {
            'conversation_id': 1
        }
        self.client.emit('join_conversation', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'error'

    def test_valid_join_conversation(self):
        data = {
            'token': self.token2
        }
        assert len(self.neo.sockets) == 0
        self.client.connect()
        self.client.emit('authenticate', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        data = {
            'conversation_id': 1
        }
        self.client.emit('join_conversation', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
