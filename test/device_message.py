from gevent import monkey
import sys
monkey.patch_all()
sys.path.insert(0, '..')
import unittest
import json
from config.loader import neo_config
from api import NeoAPI
from config.database import db
from models.User import User as UserModel
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.Device import Device
from utils.testutils import authenticate_user
from utils.testutils import authenticate_device
from models.Message import Message


class TestDeviceMessageCreate(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle, privilege="ADMIN")
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation("test")
        self.conversation.circle = self.circle
        self.device = Device(name="Papie")
        self.device.circle = self.circle
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.device_token = authenticate_device(self.api, self.device, self.device_password)
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_message(self):
        json_data = {
            "token": self.tokenAdmin,
            "device_id": self.device.id,
            "files": [],
            "conversation_id": self.conversation.id,
            "text": "test",
            "directory_name": "Tests"
        }
        response = self.api.post('/admin/device/message/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.conversation.messages) == 1

    def test_missing_parameter(self):
        json_data = {
            "token": self.tokenAdmin,
            "device_id": self.device.id,
            "files": [],
            "text": "test",
            "directory_name": "Tests"
        }
        response = self.api.post('/admin/device/message/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "token": self.tokenAdmin,
            "device_id": self.device.id,
            "files": [],
            "conversation_id": 200000,
            "text": "test",
            "directory_name": "Tests"
        }
        response = self.api.post('/admin/device/message/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "token": self.token1,
            "device_id": self.device.id,
            "files": [],
            "conversation_id": self.conversation.id,
            "text": "test",
            "directory_name": "Tests"
        }
        response = self.api.post('/admin/device/message/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestDeviceMessageDelete(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.circle2 = Circle(name="test")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle, privilege="ADMIN")
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation("test")
        self.conversation.circle = self.circle
        self.device = Device(name="Papie")
        self.device2 = Device(name="test")
        self.device2.circle = self.circle2
        self.device2_password = self.device2.get_pre_activation_password()
        self.device2.activate(self.device2.key)
        self.device.circle = self.circle
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        self.message = Message(is_user=False)
        self.message.conversation = self.conversation
        self.message.device = self.device
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.device_token = authenticate_device(self.api, self.device, self.device_password)
        self.device2_token = authenticate_device(self.api, self.device2, self.device2_password)
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_delete(self):
        json_data = {
            "device_token": self.device_token,
            "message_id": self.message.id
        }
        response = self.api.post('/device/message/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.conversation.messages) == 0

    def test_missing_parameter(self):
        json_data = {
            "device_token": self.device_token,
        }
        response = self.api.post('/device/message/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_message(self):
        json_data = {
            "device_token": self.device_token,
            "message_id": 200000
        }
        response = self.api.post('/device/message/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "device_token": self.token1,
            "message_id": self.message.id
        }
        response = self.api.post('/device/message/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_device(self):
        json_data = {
            "device_token": self.device2_token,
            "message_id": self.message.id
        }
        response = self.api.post('/device/message/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False


class TestDeviceMessageInfo(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.circle2 = Circle(name="test")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle, privilege="ADMIN")
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation("test")
        self.conversation.circle = self.circle
        self.conversation.device_access = True
        self.device = Device(name="Papie")
        self.device2 = Device(name="test")
        self.device2.circle = self.circle2
        self.device2_password = self.device2.get_pre_activation_password()
        self.device2.activate(self.device2.key)
        self.device.circle = self.circle
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        self.message = Message(is_user=False)
        self.message.conversation = self.conversation
        self.message.device = self.device
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.device_token = authenticate_device(self.api, self.device, self.device_password)
        self.device2_token = authenticate_device(self.api, self.device2, self.device2_password)
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_info(self):
        json_data = {
            "device_token": self.device_token,
            "message_id": self.message.id
        }
        response = self.api.post('/device/message/info', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True

    def test_invalid_device(self):
        json_data = {
            "device_token": self.device2_token,
            "message_id": self.message.id
        }
        response = self.api.post('/device/message/info', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "device_token": self.device_token
        }
        response = self.api.post('/device/message/info', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_message(self):
        json_data = {
            "device_token": self.device_token,
            "message_id": 200000
        }
        response = self.api.post('/device/message/info', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestDeviceMessageList(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.circle2 = Circle(name="test")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle, privilege="ADMIN")
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation("test")
        self.conversation.circle = self.circle
        self.conversation.device_access = True
        self.device = Device(name="Papie")
        self.device2 = Device(name="test")
        self.device2.circle = self.circle2
        self.device2_password = self.device2.get_pre_activation_password()
        self.device2.activate(self.device2.key)
        self.device.circle = self.circle
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        self.message = Message(is_user=False)
        self.message.conversation = self.conversation
        self.message.device = self.device
        self.message2 = Message(is_user=False)
        self.message2.conversation = self.conversation
        self.message2.device = self.device
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.device_token = authenticate_device(self.api, self.device, self.device_password)
        self.device2_token = authenticate_device(self.api, self.device2, self.device2_password)
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_list(self):
        json_data = {
            "device_token": self.device_token,
            "conversation_id": self.conversation.id,
            "quantity": 100
        }
        response = self.api.post('/device/message/list', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(response_json["content"]) == 2

    def test_invalid_device(self):
        json_data = {
            "device_token": self.device2_token,
            "conversation_id": self.conversation.id,
            "quantity": 100
        }
        response = self.api.post('/device/message/list', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False


class TestDeviceMessageUpdate(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.circle2 = Circle(name="test")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle, privilege="ADMIN")
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation("test")
        self.conversation.circle = self.circle
        self.conversation.device_access = True
        self.device = Device(name="Papie")
        self.device2 = Device(name="test")
        self.device2.circle = self.circle2
        self.device2_password = self.device2.get_pre_activation_password()
        self.device2.activate(self.device2.key)
        self.device.circle = self.circle
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        self.message = Message(is_user=False)
        self.message.conversation = self.conversation
        self.message.device = self.device
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.device_token = authenticate_device(self.api, self.device, self.device_password)
        self.device2_token = authenticate_device(self.api, self.device2, self.device2_password)
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")


    def test_valid_update(self):
        json_data = {
            "device_token": self.device_token,
            "message_id": self.message.id,
            "text_message": "44"
        }
        response = self.api.post('/device/message/update', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert self.message.text_content == "44"

    def test_invalid_message(self):
        json_data = {
            "device_token": self.device_token,
            "message_id": 200,
            "text_message": "44"
        }
        response = self.api.post('/device/message/update', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_device(self):
        json_data = {
            "device_token": self.device2_token,
            "message_id": self.message.id,
            "text_message": "44"
        }
        response = self.api.post('/device/message/update', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "device_token": self.device_token,
            "text_message": "44"
        }
        response = self.api.post('/device/message/update', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False
