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
from utils.testutils import AuthenticateUser

class TestConversationInvite(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
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
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.token3 = AuthenticateUser(self.api, self.user3, "test")

    def tearDown(self):
        db_session.delete(self.user1)
        db_session.delete(self.user2)
        db_session.delete(self.user3)
        db_session.delete(self.circle)
        db_session.commit()

    def test_valid_invite(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.conv.links) == 2

    def test_missing_conversation_id(self):
        json_data = {
            "token": self.token1,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 2000000,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": "conversation.test@gmail.com"
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user_dest(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False
        assert len(self.conv.links) == 1

    def test_already_existing_user(self):
        utc = UserToConversation()
        utc.user = self.user2
        utc.conversation = self.conv
        db_session.commit()
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False
        assert len(self.conv.links) == 2


class TestConversationUserPromote(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
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
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.token3 = AuthenticateUser(self.api, self.user3, "test")

    def tearDown(self):
        db_session.delete(self.user1)
        db_session.delete(self.user2)
        db_session.delete(self.user3)
        db_session.delete(self.circle)
        db_session.commit()

    def test_valid_promotion(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
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
        assert response_json['success'] == False

    def test_invalid_user_rights(self):
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
            "email": self.user1.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_conversation_id(self):
        json_data = {
            "token": self.token1,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 200000,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": "invalid.email@gmail.com"
        }
        response = self.api.post('/conversation/promote', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestConversationKick(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
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
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.token3 = AuthenticateUser(self.api, self.user3, "test")

    def tearDown(self):
        db_session.delete(self.user1)
        db_session.delete(self.user2)
        db_session.delete(self.user3)
        db_session.delete(self.circle)
        db_session.commit()

    def test_valid_kick(self):
        id = self.conv.id
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        c = db_session.query(Conversation).filter(Conversation.id==id).first()
        assert response.status_code == 200
        assert response_json['success'] == True
        assert c == None

    def test_invalid_user(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user_rights(self):
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
            "email": self.user1.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_conversation_id(self):
        json_data = {
            "token": self.token1,
            "email": self.user2.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 200000,
            "email": self.user3.email
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_email(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
            "email": "invalid.email@gmail.com"
        }
        response = self.api.post('/conversation/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

class TestConversationQuit(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
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
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.token3 = AuthenticateUser(self.api, self.user3, "test")

    def tearDown(self):
        db_session.delete(self.user1)
        db_session.delete(self.user2)
        db_session.delete(self.user3)
        db_session.delete(self.circle)
        db_session.commit()

    def test_valid_quit(self):
        id = self.conv.id
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        c = db_session.query(Conversation).filter(Conversation.id==id).first()
        assert response.status_code == 200
        assert response_json['success'] == True
        assert c == None

    def test_valid_quit2(self):
        self.conv.device_access = True
        db_session.commit()
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.conv.links) == 1

    def test_invalid_user(self):
        json_data = {
            "token": self.token3,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 2000000,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_change_admin(self):
        utc = UserToConversation()
        utc.user = self.user3
        utc.conversation = self.conv
        db_session.commit()
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert (utc.privilege == "ADMIN" or self.utc2.privilege == "ADMIN")


class TestConversationAddDevice(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
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
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.token3 = AuthenticateUser(self.api, self.user3, "test")

    def tearDown(self):
        db_session.delete(self.user1)
        db_session.delete(self.user2)
        db_session.delete(self.user3)
        db_session.delete(self.circle)
        db_session.commit()

    def test_valid_add(self):
        self.conv.device_access = False
        db_session.commit()
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/device/add', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert self.conv.device_access == True

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/device/add', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token2
        }
        response = self.api.post('/conversation/device/add', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

class TestConversationRemoveDevice(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelogic@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelogic2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db_session.query(UserModel).filter(UserModel.email == "testcirclelogic3@test.com").first()
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
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.token3 = AuthenticateUser(self.api, self.user3, "test")

    def tearDown(self):
        db_session.delete(self.user1)
        db_session.delete(self.user2)
        db_session.delete(self.user3)
        db_session.delete(self.circle)
        db_session.commit()

    def test_valid_remove(self):
        self.conv.device_access = True
        db_session.commit()
        json_data = {
            "token": self.token1,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/device/remove', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert self.conv.device_access == False

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "conversation_id": self.conv.id,
        }
        response = self.api.post('/conversation/device/remove', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token2
        }
        response = self.api.post('/conversation/device/remove', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False
