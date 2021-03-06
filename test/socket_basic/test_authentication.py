import unittest
from flask_socketio import SocketIOTestClient
from config.loader import neo_config
from api import NeoAPI, sockets, socketio
from config.database import db
from utils.testutils import authenticate_user
from models.User import User as UserModel
from gevent import monkey
monkey.patch_all()


class SocketioAuthenticate(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        self.neo = NeoAPI(neo_config)
        self.api = self.neo.activate_testing()
        self.client = SocketIOTestClient(self.neo.app, socketio)
        self.client2 = SocketIOTestClient(self.neo.app, socketio)
        self.client.disconnect()
        self.client2.disconnect()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "te@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="te@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")

    def tearDown(self):
        self.client.disconnect()
        self.client2.disconnect()

    def test_valid_connection(self):
        assert len(sockets) == 0
        self.client.connect()
        assert len(sockets) == 0
        self.client2.connect()
        assert len(sockets) == 0

    def test_valid_authentication(self):
        data = {
            'token': self.token1
        }
        assert len(sockets) == 0
        self.client.connect()
        self.client.emit('authenticate', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        if not self.neo.config.use_redis:
            assert len(sockets) == 1

    def test_invalid_authentication(self):
        data = {
            'token': '333444'
        }
        assert len(sockets) == 0
        self.client.connect()
        self.client.emit('authenticate', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'error'
