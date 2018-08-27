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
from utils.testutils import authenticate_user
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation as UTC


class TestConversationCreate(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testconversation@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testconversation@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testconversation2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testconversation2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_circle(self):
        self.circle = Circle("TESTCONVCREATE")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db.session.commit()

    def test_valid_creation(self):
        json_data = {
            "conversation_name": "ConversationTest",
            "circle_id": self.circle.id,
            "token": self.tokenAdmin
        }
        response = self.api.post('/admin/conversation/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert response_json['content']["name"] == "ConversationTest"

    def test_missing_parameter(self):
        json_data = {
            "circle_id": self.circle.id,
            "token": self.tokenAdmin
        }
        response = self.api.post('/admin/conversation/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "conversation_name": "ConversationTest",
            "circle_id": self.circle.id,
            "token": self.token1
        }
        response = self.api.post('/admin/conversation/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_circle(self):
        json_data = {
            "conversation_name": "ConversationTest",
            "circle_id": 2000000,
            "token": self.tokenAdmin
        }
        response = self.api.post('/admin/conversation/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestConversationDelete(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testconversationdelete@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testconversationdelete@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testconversationdelete2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testconversationdelete2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle()
        self.create_conversation()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_conversation(self):
        self.conv = Conversation(name="TESTCONVDELETE")
        self.conv.circle = self.circle
        self.utc1 = UTC()
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        self.utc2 = UTC()
        self.utc2.user = self.user2
        self.utc2.conversation = self.conv
        db.session.commit()

    def create_circle(self):
        self.circle = Circle("TESTCONVDELETE")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db.session.commit()

    def test_valid_delete(self):
        id = self.conv.id
        json_data = {
            "conversation_id": self.conv.id,
            "token": self.tokenAdmin
        }
        response = self.api.post('/admin/conversation/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        c = db.session.query(Conversation).filter(Conversation.id==id).first()
        assert response.status_code == 200
        assert response_json['success'] == True
        assert c == None

    def test_missing_parameter(self):
        json_data = {
            "token": self.tokenAdmin
        }
        response = self.api.post('/admin/conversation/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "conversation_id": self.conv.id,
            "token": self.token1
        }
        response = self.api.post('/admin/conversation/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "conversation_id": 2000000,
            "token": self.tokenAdmin
        }
        response = self.api.post('/admin/conversation/delete', data=json.dumps(json_data),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestConversationInfo(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testconversationinfo@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testconversationinfo2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testconversationinfo3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle()
        self.create_conversation()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_conversation(self):
        self.conv = Conversation(name="ConversationInfoTest")
        self.conv.circle = self.circle
        self.utc1 = UTC()
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        self.utc2 = UTC()
        self.utc2.user = self.user2
        self.utc2.conversation = self.conv
        db.session.commit()

    def create_circle(self):
        self.circle = Circle("TESTCONVDELETE")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db.session.commit()

    def test_valid_info(self):
        json_data = {
            "conversation_id": self.conv.id,
            "token": self.token1
        }
        response = self.api.post('/conversation/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert response_json['content']["name"] == "ConversationInfoTest"

    def test_invalid_user(self):
        json_data = {
            "conversation_id": self.conv.id,
            "token": self.token3
        }
        response = self.api.post('/conversation/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "conversation_id": 200000,
            "token": self.token1
        }
        response = self.api.post('/conversation/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/conversation/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestConversationDeviceInfo(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        db.session.query(UserModel).delete()
        db.session.commit()

    def test_valid_info(self):
        assert True == True


class TestConversationList(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testconversationinfo@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testconversationinfo2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testconversationinfo3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle()
        self.conv1 = Conversation(name="ConversationInfoTest")
        self.conv2 = Conversation(name="ConversationInfoTest2")
        self.conv3 = Conversation(name="ConversationInfoTest2")
        self.utc1 = UTC()
        self.utc2 = UTC()
        self.utc3 = UTC()
        self.utc4 = UTC()
        self.create_conversation(self.conv1, self.user1, self.user2, self.utc1, self.utc2, self.circle)
        self.create_conversation(self.conv3, self.user1, self.user2, UTC(), UTC(), self.circle)
        self.create_conversation(self.conv2, self.user2, self.user3, self.utc3, self.utc4, self.circle2)
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_conversation(self, conv, u1, u2, utc1, utc2, circle):
        conv.circle = circle
        utc1.user = u1
        utc1.conversation = conv
        utc2.user = u2
        utc2.conversation = conv
        db.session.commit()

    def create_circle(self):
        self.circle = Circle("TESTCONVLIST")
        self.circle2 = Circle("TESTCONVLIST2")
        self.link1 = UserToCircle()
        self.link2 = UserToCircle()
        self.link3 = UserToCircle()
        self.link4 = UserToCircle()
        self.link1.user = self.user1
        self.link1.circle = self.circle
        self.link2.user = self.user2
        self.link2.circle = self.circle
        self.link3.user = self.user3
        self.link3.circle = self.circle2
        self.link4.user = self.user2
        self.link4.circle = self.circle2
        db.session.commit()

    def test_valid_list(self):
        json_data = {
            "circle_id": self.circle.id,
            "token": self.token1
        }
        response = self.api.post('/conversation/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(response_json['content']) == 2

    def test_valid_list2(self):
        json_data = {
            "circle_id": self.circle2.id,
            "token": self.token3
        }
        response = self.api.post('/conversation/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(response_json['content']) == 1

    def test_invalid_user(self):
        json_data = {
            "circle_id": self.circle.id,
            "token": self.token3
        }
        response = self.api.post('/conversation/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_user_without_conv(self):
        json_data = {
            "circle_id": self.circle.id,
            "token": self.tokenAdmin
        }
        response = self.api.post('/conversation/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/conversation/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_circle(self):
        json_data = {
            "circle_id": 200000,
            "token": self.token1
        }
        response = self.api.post('/conversation/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestConversationDeviceList(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        db.session.query(UserModel).delete()
        db.session.commit()

    def test_valid_list(self):
        assert True == True


class TestConversationUpdate(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testconversationinfo@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testconversationinfo2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testconversationinfo3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testconversationinfo3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle()
        self.create_conversation()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.token3 = authenticate_user(self.api, self.user3, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_conversation(self):
        self.conv = Conversation(name="ConversationUpdateTest")
        self.conv.circle = self.circle
        self.utc1 = UTC(privilege="ADMIN")
        self.utc1.user = self.user1
        self.utc1.conversation = self.conv
        self.utc2 = UTC()
        self.utc2.user = self.user2
        self.utc2.conversation = self.conv
        db.session.commit()

    def create_circle(self):
        self.circle = Circle("TESTCONVUPDATE")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db.session.commit()

    def test_valid_update(self):
        json_data = {
            "conversation_id": self.conv.id,
            "conversation_name": "UPDATEDCONV",
            "device_access": True,
            "token": self.token1
        }
        response = self.api.post('/conversation/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert response_json["content"]["name"] == "UPDATEDCONV"
        assert response_json["content"]["device_access"] == True

    def test_invalid_user(self):
        json_data = {
            "conversation_id": self.conv.id,
            "conversation_name": "UPDATEDCONV",
            "token": self.token2
        }
        response = self.api.post('/conversation/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_invalid_user2(self):
        json_data = {
            "conversation_id": self.conv.id,
            "conversation_name": "UPDATEDCONV",
            "token": self.tokenAdmin
        }
        response = self.api.post('/conversation/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token2
        }
        response = self.api.post('/conversation/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False