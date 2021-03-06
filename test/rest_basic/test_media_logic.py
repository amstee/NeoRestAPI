import unittest
import json
from config.loader import neo_config
from api import NeoAPI
from config.database import db
from models.User import User as UserModel
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from utils.testutils import authenticate_user, authenticate_device
from models.Message import Message
from models.Media import Media
import io
import shutil
import os
from models.Device import Device
from datauri import DataURI
from gevent import monkey
monkey.patch_all()


class TestMediaCreate(unittest.TestCase):
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
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")
        self.tokenDevice = authenticate_device(self.api, self.device, self.device_password)

    def test_valid_create(self):
        json_data = {
            'token': self.token1,
            'medias': [
                {
                    "purpose": "testing",
                    "name": "test_file.txt"
                },
                {
                    "purpose": "picture",
                    "name": "test_file2.txt"
                }
            ],
        }
        response = self.api.post('/media/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        assert len(response_json['media_list']) == 2
        headers = {
            'content-type': 'multipart/form-data',
            'Authorization': self.token1
        }
        data = {
            'file': (io.BytesIO(b"user1 sent a file 22"), 'test_file.txt')
        }
        mid = response_json['media_list'][0]['id']
        response = self.api.post('/media/upload/' + str(response_json['media_list'][0]['id']), data=data,
                                 headers=headers)
        response_json = json.loads(response.data)
        assert response_json["success"] is True
        assert os.path.exists('user_files' + os.path.sep + 'user_' + str(self.user1.id) + os.path.sep)
        json_data = {
            "token": self.token1,
            "media_id": mid
        }
        response = self.api.post('/media/retrieve', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        response_file = DataURI(response_json['data'])
        assert response_json['success']
        assert response_file.data == b"user1 sent a file 22"

    def tearDown(self):
        if os.path.exists("user_files"):
            shutil.rmtree('user_files')


class TestDeviceMediaCreate(unittest.TestCase):
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
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")
        self.tokenDevice = authenticate_device(self.api, self.device, self.device_password)

    def test_valid_create(self):
        json_data = {
            'device_token': self.tokenDevice,
            'medias': [
                {
                    "purpose": "testing",
                    "name": "test_file.txt"
                },
                {
                    "purpose": "picture",
                    "name": "test_file2.txt"
                }
            ],
        }
        response = self.api.post('/media/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        assert len(response_json['media_list']) == 2
        headers = {
            'content-type': 'multipart/form-data',
            'Authorization': self.tokenDevice
        }
        data = {
            'file': (io.BytesIO(b"user1 sent a file 225"), 'test_file.txt')
        }
        mid = response_json['media_list'][0]['id']
        response = self.api.post('/media/upload/' + str(response_json['media_list'][0]['id']), data=data,
                                 headers=headers)
        response_json = json.loads(response.data)
        assert response_json["success"] is True
        assert os.path.exists('user_files' + os.path.sep + 'device_' + str(self.device.id) + os.path.sep)
        json_data = {
            "device_token": self.tokenDevice,
            "media_id": mid
        }
        response = self.api.post('/media/retrieve', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        response_file = DataURI(response_json['data'])
        assert response_json['success']
        assert response_file.data == b"user1 sent a file 225"

    def tearDown(self):
        if os.path.exists("user_files"):
            shutil.rmtree('user_files')


class TestMediaRequest(unittest.TestCase):
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
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.message = Message()
        self.message.conversation = self.conversation
        self.message.link = self.linkConversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_request(self):
        json_data = {
            'token': self.token1,
            'files': ["test_file.txt"],
            'conversation_id': self.conversation.id
        }
        response = self.api.post('/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        assert len(response_json['media_list']) == 1
        headers = {
            'content-type': 'multipart/form-data',
            'Authorization': self.token1
        }
        data = {
            'file': (io.BytesIO(b"user1 sent a file"), 'test_file.txt')
        }
        media_id = response_json['media_list'][0]['id']
        response = self.api.post('/media/upload/' + str(response_json['media_list'][0]['id']), data=data,
                                 headers=headers)
        response_json = json.loads(response.data)
        assert response_json["success"] is True
        assert os.path.exists('user_files' + os.path.sep + 'conversation_' + str(self.conversation.id) + os.path.sep)
        json_data = {
            "token": self.token1,
            "media_id": media_id
        }
        response = self.api.post('/media/retrieve', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        response_file = DataURI(response_json['data'])
        assert response_json['success']
        assert response_file.data == b"user1 sent a file"

    def tearDown(self):
        if os.path.exists("user_files"):
            shutil.rmtree('user_files')


class TestDeviceMediaRequest(unittest.TestCase):
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
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")
        self.tokenDevice = authenticate_device(self.api, self.device, self.device_password)

    def test_valid_request(self):
        json_data = {
            'device_token': self.tokenDevice,
            'files': ["test_file.txt"],
            'conversation_id': self.conversation.id
        }
        response = self.api.post('/device/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        assert len(response_json['media_list']) == 1
        headers = {
            'content-type': 'multipart/form-data',
            'Authorization': self.tokenDevice
        }
        data = {
            'file': (io.BytesIO(b"device sent a file"), 'test_file.txt')
        }
        media_id = response_json['media_list'][0]['id']
        response = self.api.post('/media/upload/' + str(response_json['media_list'][0]['id']),
                                 data=data, headers=headers)
        response_json = json.loads(response.data)
        assert response_json["success"] is True
        assert os.path.exists('user_files' + os.path.sep + 'conversation_' + str(self.conversation.id) + os.path.sep)
        json_data = {
            "device_token": self.tokenDevice,
            "media_id": media_id
        }
        response = self.api.post('/media/retrieve', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        response_file = DataURI(response_json['data'])
        assert response_json['success']
        assert response_file.data == b"device sent a file"

    def tearDown(self):
        shutil.rmtree('user_files')


class TestMediaUpload(unittest.TestCase):
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
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle)
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.message = Message()
        self.message.conversation = self.conversation
        self.message.link = self.linkConversation
        self.media = Media('test', '.txt', 'test.txt')
        self.media.message = self.message
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_upload(self):
        json_data = {
            'token': self.token1,
            'files': ["test_file.txt"],
            'conversation_id': self.conversation.id
        }
        response = self.api.post('/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        assert len(response_json['media_list']) == 1
        headers = {
            'content-type': 'multipart/form-data',
            'Authorization': self.token1
        }
        data = {
            'file': (io.BytesIO(b"user1 sent a file"), 'test_file.txt')
        }
        response = self.api.post('/media/upload/' + str(response_json['media_list'][0]['id']),
                                 data=data, headers=headers)
        response_json = json.loads(response.data)
        assert response_json["success"] is True
        assert os.path.exists('user_files' + os.path.sep + 'conversation_' + str(self.conversation.id) + os.path.sep)

    def tearDown(self):
        if os.path.exists("user_files"):
            shutil.rmtree('user_files')


class TestDeviceMediaUpload(unittest.TestCase):
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
        self.device_password = self.device.get_pre_activation_password()
        self.device.activate(self.device.key)
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")
        self.tokenDevice = authenticate_device(self.api, self.device, self.device_password)

    def test_valid_upload_message(self):
        json_data = {
            'device_token': self.tokenDevice,
            'files': ["test_file.txt"],
            'conversation_id': self.conversation.id
        }
        response = self.api.post('/device/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        assert len(response_json['media_list']) == 1
        headers = {
            'content-type': 'multipart/form-data',
            'Authorization': self.tokenDevice
        }
        data = {
            'file': (io.BytesIO(b"device sent a file"), 'test_file.txt')
        }
        response = self.api.post('/media/upload/' + str(response_json['media_list'][0]['id']),
                                 data=data, headers=headers)
        response_json = json.loads(response.data)
        assert response_json["success"] is True
        assert os.path.exists('user_files' + os.path.sep + 'conversation_' + str(self.conversation.id) + os.path.sep)

    def test_invalid_upload_message(self):
        json_data = {
            'device_token': self.tokenDevice,
            'files': ["test_file.txt"],
            'conversation_id': self.conversation.id
        }
        response = self.api.post('/device/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        assert len(response_json['media_list']) == 1
        headers = {
            'content-type': 'multipart/form-data',
            'Authorization': self.tokenDevice
        }
        data = {
            'file': (io.BytesIO(b"device sent a file 2"), 'test_file.txt')
        }
        response = self.api.post('/media/upload/' + "999", data=data, headers=headers)
        response_json = json.loads(response.data)
        assert response_json["success"] is False

    def tearDown(self):
        if os.path.exists("user_files"):
            shutil.rmtree('user_files')
