import unittest
import sys
from flask_socketio import SocketIOTestClient
sys.path.insert(0, '..')
from api import neoapi
from config.database import db_session
from utils.testutils import AuthenticateUser
from models.User import User as UserModel
from models.UserToCircle import UserToCircle
from models.Circle import Circle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from models.Device import Device
from utils.testutils import AuthenticateDevice


class SocketioRoomConversation(unittest.TestCase):
    def setUp(self):
        self.neo = neoapi()
        self.api = self.neo.activate_testing()
        self.client = SocketIOTestClient(self.neo.app, self.neo.socketio)
        self.client.disconnect()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "te@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="te@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "tea@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="tea@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle, privilege="ADMIN")
        self.conversation = Conversation("test", device_access=True)
        self.conversation.device_access = True
        self.conversation.circle = self.circle
        self.link2 = UserToConversation(user=self.user2, conversation=self.conversation)
        self.device = Device(name="Papie")
        self.device.circle = self.circle
        self.device_password = self.device.getPreActivationPassword()
        self.device.activate(self.device.key)
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.device_token = AuthenticateDevice(self.api, self.device, self.device_password)
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

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
            'conversation_id': self.conversation.id
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
            'conversation_id': self.conversation.id
        }
        self.client.emit('join_conversation', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'

    def test_valid_device_join_conversation(self):
        data = {
            'token': self.device_token
        }
        assert len(self.neo.sockets) == 0
        self.client.connect()
        self.client.emit('authenticate', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        data = {
            'conversation_id': self.conversation.id
        }
        self.client.emit('join_conversation', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'

    def test_device_join_without_conv_access(self):
        self.conversation.device_access = False
        db_session.commit()
        data = {
            'token': self.device_token
        }
        assert len(self.neo.sockets) == 0
        self.client.connect()
        self.client.emit('authenticate', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        data = {
            'conversation_id': self.conversation.id
        }
        self.client.emit('join_conversation', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'error'

    def test_valid_leave_conversation(self):
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
            'conversation_id': self.conversation.id
        }
        self.client.emit('join_conversation', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        self.client.emit('leave_conversation', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'

    def test_invalid_leave_conversation(self):
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
            'conversation_id': self.conversation.id
        }
        self.client.emit('leave_conversation', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'


class SocketioRoomCircle(unittest.TestCase):
    def setUp(self):
        self.neo = neoapi()
        self.api = self.neo.activate_testing()
        self.client = SocketIOTestClient(self.neo.app, self.neo.socketio)
        self.client2 = SocketIOTestClient(self.neo.app, self.neo.socketio)
        self.deviceClient = SocketIOTestClient(self.neo.app, self.neo.socketio)
        self.client.disconnect()
        self.client2.disconnect()
        self.deviceClient.disconnect()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "te@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="te@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "tea@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="tea@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle, privilege="ADMIN")
        self.conversation = Conversation("test")
        self.conversation.device_access = True
        self.conversation.circle = self.circle
        self.link = UserToConversation(user=self.user1, conversation=self.conversation, privilege='ADMIN')
        self.link2 = UserToConversation(user=self.user2, conversation=self.conversation)
        self.device = Device(name="Papie")
        self.device.circle = self.circle
        self.device_password = self.device.getPreActivationPassword()
        self.device.activate(self.device.key)
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.device_token = AuthenticateDevice(self.api, self.device, self.device_password)
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def tearDown(self):
        self.client.disconnect()
        self.client2.disconnect()
        self.deviceClient.disconnect()

    def test_valid_device_join_circle(self):
        data = {
            'token': self.device_token
        }
        assert len(self.neo.sockets) == 0
        self.deviceClient.connect()
        self.deviceClient.emit('authenticate', data, json=True)
        res = self.deviceClient.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        data = {
            'circle_id': self.circle.id
        }
        self.deviceClient.emit('join_circle', data, json=True)
        res = self.deviceClient.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'

    def test_valid_join_circle(self):
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
            'circle_id': self.circle.id
        }
        self.client.emit('join_circle', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'

    def test_invalid_join_circle(self):
        data = {
            'token': self.token2
        }
        assert len(self.neo.sockets) == 0
        self.client2.connect()
        self.client2.emit('authenticate', data, json=True)
        res = self.client2.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        data = {
            'circle_id': self.circle.id
        }
        self.client2.emit('join_circle', data, json=True)
        res = self.client2.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'error'

    def test_valid_leave_circle(self):
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
            'circle_id': self.circle.id
        }
        self.client.emit('join_circle', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'
        self.client.emit('leave_circle', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'

    def test_invalid_leave_circle(self):
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
            'circle_id': self.circle.id
        }
        self.client.emit('leave_circle', data, json=True)
        res = self.client.get_received()
        assert len(res) == 1
        assert res[0]['name'] == 'success'

