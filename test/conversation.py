import unittest
import sys
import json

sys.path.insert(0,'..')
from api import neoapi
from config.database import db_session
from models.User import User as UserModel
from utils.testutils import AuthenticateUser
from models.Circle import Circle
from models.UserToCircle import UserToCircle

class TestConversationCreate(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        self.user1 = db_session.query(UserModel).filter(UserModel.email == "testconversation@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testconversation@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db_session.query(UserModel).filter(UserModel.email == "testconversation2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testconversation2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        db_session.commit()
        self.token1 = AuthenticateUser(self.api, self.user1, "test")
        self.token2 = AuthenticateUser(self.api, self.user2, "test")
        self.tokenAdmin = AuthenticateUser(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_circle(self):
        self.circle = Circle("TESTDELETION")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db_session.commit()

    def test_valid_creation(self):
        json_data = {
            "conversation_name": "ConversationTest",
            "circle_id": self.circle.id,
            "token": self.tokenAdmin
        }
        response = self.api.post('/conversation/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert response_json['content']["name"] == "ConversationTest"

    def test_invalid_user(self):
        json_data = {
            "conversation_name": "ConversationTest",
            "circle_id": self.circle.id,
            "token": self.token1
        }
        response = self.api.post('/conversation/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

class TestConversationDelete(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

class TestConversationInfo(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

class TestConversationDeviceInfo(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

class TestConversationList(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

class TestConversationDeviceList(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

class TestConversationUpdate(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()