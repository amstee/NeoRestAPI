import unittest
import sys
from flask_socketio import SocketIOTestClient
import json
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
        self.client2 = SocketIOTestClient(self.neo.app, self.neo.socketio)
        self.client.disconnect()
        self.client2.disconnect()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "te@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="te@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.token1 = AuthenticateUser(self.api, self.user1, "test")

    def tearDown(self):
        self.client.disconnect()
        self.client2.disconnect()

    def test_account_modify(self):
        data = {
            'token': self.token1
        }
        assert len(self.neo.sockets) == 0
        self.client.connect()
        self.client.emit('authenticate', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        json_data = {
            "token": self.token1,
            'first_name': 'ne'
        }
        response = self.api.post('/account/modify', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response_json['success'] is True
        res = self.client.get_received()
        assert len(res) == 1