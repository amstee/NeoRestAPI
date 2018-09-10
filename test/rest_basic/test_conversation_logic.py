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
from utils.testutils import authenticate_user
from gevent import monkey
monkey.patch_all()


class TestConversationInvite(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testcirclelogic3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="TestConversationinvite")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.link2 = UserToCircle()
        self.link2.user = self.user2
        self.link2.circle = self.circle
        self.conv = Conversation()
        self.conv.circle = self.circle
        self.utc1 = UserToConversation(privilege="ADMIN")
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.delete(self.user3)
        db.session.delete(self.circle)
        db.session.commit()

    def test_valid_invite(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success']
        assert len(self.conv.links) == 2

    def test_missing_conversation_id(self):
        json_data = {
            "token": self.token1,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_missing_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 2000000,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": "conversation.test@gmail.com"
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_user_dest(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']
        assert len(self.conv.links) == 1

    def test_already_existing_user(self):
        utc = UserToConversation()
        utc.user = self.user2
        utc.conversation = self.conv
        db.session.commit()
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']
        assert len(self.conv.links) == 2


class TestConversationUserPromote(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testcirclelogic3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="TestConversationinvite")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.link2 = UserToCircle()
        self.link2.user = self.user2
        self.link2.circle = self.circle
        self.conv = Conversation()
        self.conv.circle = self.circle
        self.utc1 = UserToConversation(privilege="ADMIN")
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        self.utc2 = UserToConversation(privilege="STANDARD")
        self.utc2.user = self.user2
        self.utc2.conversation = self.conv
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.delete(self.user3)
        db.session.delete(self.circle)
        db.session.commit()

    def test_valid_promotion(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success']
        assert len(self.conv.links) == 2
        assert self.utc2.privilege == "ADMIN"
        assert self.utc1.privilege == "STANDARD"

    def test_invalid_user(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_user_rights(self):
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
            "email": self.user1.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert not response_json['success']

    def test_missing_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_missing_conversation_id(self):
        json_data = {
            "token": self.token1,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 200000,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": "invalid.email@gmail.com"
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']


class TestConversationKick(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testcirclelogic3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="TestConversationinvite")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.link2 = UserToCircle()
        self.link2.user = self.user2
        self.link2.circle = self.circle
        self.conv = Conversation()
        self.conv.circle = self.circle
        self.utc1 = UserToConversation(privilege="ADMIN")
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        self.utc2 = UserToConversation(privilege="STANDARD")
        self.utc2.user = self.user2
        self.utc2.conversation = self.conv
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.delete(self.user3)
        db.session.delete(self.circle)
        db.session.commit()

    def test_valid_kick(self):
        conv_id = self.conv.id
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        c = db.session.query(Conversation).filter(Conversation.id == conv_id).first()
        assert response.status_code == 200
        assert response_json['success']
        assert c is None

    def test_invalid_user(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_user_rights(self):
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
            "email": self.user1.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert not response_json['success']

    def test_missing_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_missing_conversation_id(self):
        json_data = {
            "token": self.token1,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 200000,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": "invalid.email@gmail.com"
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']


class TestConversationQuit(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testcirclelogic3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="TestConversationinvite")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.link2 = UserToCircle()
        self.link2.user = self.user2
        self.link2.circle = self.circle
        self.conv = Conversation()
        self.conv.circle = self.circle
        self.utc1 = UserToConversation(privilege="ADMIN")
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        self.utc2 = UserToConversation(privilege="STANDARD")
        self.utc2.user = self.user2
        self.utc2.conversation = self.conv
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.delete(self.user3)
        db.session.delete(self.circle)
        db.session.commit()

    def test_valid_quit(self):
        conv_id = self.conv.id
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        c = db.session.query(Conversation).filter(Conversation.id == conv_id).first()
        assert response.status_code == 200
        assert response_json['success']
        assert c is None

    def test_valid_quit2(self):
        self.conv.device_access = True
        db.session.commit()
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        c = db.session.query(UserToConversation).filter(UserToConversation.conversation_id == self.conv.id).filter(
            UserToConversation.user_id == self.user2.id).first()
        assert response.status_code == 200
        assert response_json['success']
        assert c is None
        assert len(self.conv.links) == 1

    def test_invalid_user(self):
        json_data = {
            "token": self.token3,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 2000000,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_change_admin(self):
        utc = UserToConversation()
        utc.user = self.user3
        utc.conversation = self.conv
        db.session.commit()
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success']
        assert (utc.privilege == "ADMIN" or self.utc2.privilege == "ADMIN")


class TestConversationAddDevice(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testcirclelogic3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="TestConversationinvite")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.link2 = UserToCircle()
        self.link2.user = self.user2
        self.link2.circle = self.circle
        self.conv = Conversation()
        self.conv.circle = self.circle
        self.utc1 = UserToConversation(privilege="ADMIN")
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        self.utc2 = UserToConversation(privilege="STANDARD")
        self.utc2.user = self.user2
        self.utc2.conversation = self.conv
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.delete(self.user3)
        db.session.delete(self.circle)
        db.session.commit()

    def test_valid_add(self):
        self.conv.device_access = False
        db.session.commit()
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/device/set', data=json.dumps(json_data),
                                content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success']
        assert self.conv.device_access

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/device/set', data=json.dumps(json_data),
                                content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert not response_json['success']

    def test_missing_parameter(self):
        json_data = {
            "token": self.token2
        }
        response = self.api.post('/conversation/device/set', data=json.dumps(json_data),
                                content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']


class TestConversationRemoveDevice(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testcirclelogic3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="TestConversationinvite")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.link2 = UserToCircle()
        self.link2.user = self.user2
        self.link2.circle = self.circle
        self.conv = Conversation()
        self.conv.circle = self.circle
        self.utc1 = UserToConversation(privilege="ADMIN")
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        self.utc2 = UserToConversation(privilege="STANDARD")
        self.utc2.user = self.user2
        self.utc2.conversation = self.conv
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.delete(self.user3)
        db.session.delete(self.circle)
        db.session.commit()

    def test_valid_remove(self):
        self.conv.device_access = True
        db.session.commit()
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/device/set', data=json.dumps(json_data),
                                content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success']
        assert not self.conv.device_access

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/device/set', data=json.dumps(json_data),
                                content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert not response_json['success']

    def test_missing_parameter(self):
        json_data = {
            "token": self.token2
        }
        response = self.api.post('/conversation/device/set', data=json.dumps(json_data),
                                content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']
