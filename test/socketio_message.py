import unittest
import sys
from flask_socketio import SocketIOTestClient
sys.path.insert(0, '..')
from api import neoapi
from config.database import db_session
from utils.testutils import AuthenticateUser
from utils.testutils import AuthenticateDevice
from models.User import User as UserModel
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from models.Device import Device


class SocketioMessageEvents(unittest.TestCase):
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
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
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

    def test_valid_message(self):
        data = {
            'token': self.token1
        }
        assert len(self.neo.sockets) == 0
        self.client.connect()
        self.client2.connect()
        self.deviceClient.connect()
        self.client.emit('authenticate', data, json=True)
        self.client2.emit('authenticate', {'token': self.token2}, json=True)
        self.deviceClient.emit('authenticate', {'token': self.device_token}, json=True)
        res1 = self.client.get_received()
        res2 = self.client2.get_received()
        res3 = self.deviceClient.get_received()
        assert len(res1) == 1
        assert res1[0]['name'] == 'success'
        assert len(res2) == 1
        assert res2[0]['name'] == 'success'
        assert len(res3) == 1
        assert res3[0]['name'] == 'success'
        self.client.emit('join_conversation',
                         {'conversation_id': self.conversation.id}, json=True)
        self.client2.emit('join_conversation',
                         {'conversation_id': self.conversation.id}, json=True)
        self.deviceClient.emit('join_conversation',
                         {'conversation_id': self.conversation.id}, json=True)
        res1 = self.client.get_received()
        res2 = self.client2.get_received()
        res3 = self.deviceClient.get_received()
        assert len(res1) == 1
        assert res1[0]['name'] == 'success'
        assert len(res2) == 1
        assert res2[0]['name'] == 'success'
        assert len(res3) == 1
        assert res3[0]['name'] == 'success'
        sock = {
            'conversation_id': self.conversation.id,
            'text_message': 'test web socket'
        }
        self.client.emit('message', sock, json=True)
        err = self.client.get_received()
        res = self.client2.get_received()
        res2 = self.deviceClient.get_received()
        assert len(err) == 2
        assert len(res) == 1
        assert len(res2) == 1
        self.client.disconnect()
        self.client2.disconnect()
        self.deviceClient.disconnect()

    def test_valid_message_from_device(self):
        data = {
            'token': self.token1
        }
        assert len(self.neo.sockets) == 0
        self.client.connect()
        self.client2.connect()
        self.deviceClient.connect()
        self.client.emit('authenticate', data, json=True)
        self.client2.emit('authenticate', {'token': self.token2}, json=True)
        self.deviceClient.emit('authenticate', {'token': self.device_token}, json=True)
        res1 = self.client.get_received()
        res2 = self.client2.get_received()
        res3 = self.deviceClient.get_received()
        assert len(res1) == 1
        assert res1[0]['name'] == 'success'
        assert len(res2) == 1
        assert res2[0]['name'] == 'success'
        assert len(res3) == 1
        assert res3[0]['name'] == 'success'
        self.client.emit('join_conversation',
                         {'conversation_id': self.conversation.id}, json=True)
        self.client2.emit('join_conversation',
                         {'conversation_id': self.conversation.id}, json=True)
        self.deviceClient.emit('join_conversation',
                         {'conversation_id': self.conversation.id}, json=True)
        res1 = self.client.get_received()
        res2 = self.client2.get_received()
        res3 = self.deviceClient.get_received()
        assert len(res1) == 1
        assert res1[0]['name'] == 'success'
        assert len(res2) == 1
        assert res2[0]['name'] == 'success'
        assert len(res3) == 1
        assert res3[0]['name'] == 'success'
        sock = {
            'conversation_id': self.conversation.id,
            'text_message': 'test web socket'
        }
        self.deviceClient.emit('message', sock, json=True)
        err = self.client.get_received()
        res = self.client2.get_received()
        res2 = self.deviceClient.get_received()
        assert len(err) == 1
        assert len(res) == 1
        assert len(res2) == 2


