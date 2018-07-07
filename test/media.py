import unittest
import sys
import json

sys.path.insert(0,'..')
from api import neoapi
from config.database import db_session
from models.User import User as UserModel
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from utils.testutils import AuthenticateUser, AuthenticateDevice
from models.Message import Message
from models.Media import Media
from models.Device import Device


class TestMediaInfo(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.message = Message()
        self.message.conversation = self.conversation
        self.message.link = self.linkConversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_info(self):
        json_data = {
            'token': self.token1,
            'media_id': self.media.id
        }
        response = self.api.post('/media/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True

    def test_invalid_info(self):
        json_data = {
            'token': self.token2,
            'media_id': self.media.id
        }
        response = self.api.post('/media/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] is False


class TestMediaInfoAdmin(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation, privilege="STANDARD")
        self.message = Message()
        self.message.conversation = self.conversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_info(self):
        json_data = {
            'token': self.tokenAdmin,
            'media_id': self.media.id
        }
        response = self.api.post('/admin/media/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert 'directory' in response_json['content']

    def test_invalid_info(self):
        json_data = {
            'token': self.token1,
            'media_id': self.media.id
        }
        response = self.api.post('/admin/media/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestMediaDelete(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation, privilege="STANDARD")
        self.message = Message()
        self.message.conversation = self.conversation
        self.message.link = self.linkConversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_delete(self):
        json_data = {
            'token': self.tokenAdmin,
            'media_id': self.media.id,
        }
        data = self.media.id
        response = self.api.post('/admin/media/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        temp = db_session.query(Media).filter(Media.id == data).first()
        assert temp is None


class TestMediaList(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.message = Message()
        self.message.conversation = self.conversation
        self.message.link = self.linkConversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_list(self):
        json_data = {
            'token': self.token1,
            'message_id': self.message.id
        }
        response = self.api.post('/media/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True

    def test_invalid_list(self):
        json_data = {
            'token': self.token2,
            'message_id': self.message.id
        }
        response = self.api.post('/media/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] is False


class TestMediaUpdate(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation, privilege="STANDARD")
        self.message = Message()
        self.message.link = self.linkConversation
        self.message.conversation = self.conversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_update(self):
        json_data = {
            'token': self.tokenAdmin,
            'media_id': self.media.id,
            'identifier': 't'
        }
        response = self.api.post('/admin/media/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert self.media.identifier == 't'

    def test_invalid_update(self):
        json_data = {
            'token': self.token1,
            'media_id': self.media.id,
            'identifier': 't'
        }
        response = self.api.post('/admin/media/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestDeviceMediaList(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle, device_access=True)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.message = Message()
        self.message.conversation = self.conversation
        self.message.link = self.linkConversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        self.device = Device(name="Papie")
        self.device.circle = self.circle
        self.device_password = self.device.getPreActivationPassword()
        self.device.activate(self.device.key)
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")
        self.tokenDevice = AuthenticateDevice(self.api, self.device, self.device_password)

    def test_valid_list(self):
        json_data = {
            'device_token': self.tokenDevice,
            'message_id': self.message.id
        }
        response = self.api.post('/device/media/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True

    def test_invalid_list(self):
        json_data = {
            'device_token': self.token1,
            'message_id': self.message.id
        }
        response = self.api.post('/device/media/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] is False


class TestDeviceMediaInfo(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testmessage@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testmessage@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testmessage2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testmessage2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="Mamie")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle, device_access=True)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.message = Message()
        self.message.conversation = self.conversation
        self.message.link = self.linkConversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        self.device = Device(name="Papie")
        self.device.circle = self.circle
        self.device_password = self.device.getPreActivationPassword()
        self.device.activate(self.device.key)
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")
        self.tokenDevice = AuthenticateDevice(self.api, self.device, self.device_password)

    def test_valid_info(self):
        json_data = {
            'device_token': self.tokenDevice,
            'media_id': self.media.id
        }
        response = self.api.post('/device/media/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True

    def test_invalid_info(self):
        json_data = {
            'device_token': self.token1,
            'media_id': self.media.id
        }
        response = self.api.post('/device/media/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] is False



