import unittest
import sys
import json

sys.path.insert(0,'..')
from config.loader import neo_config
from api import NeoAPI
from config.database import db
from models.User import User as UserModel
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.Circle import Circle
from models.UserToConversation import UserToConversation
from utils.testutils import authenticate_user


class TestFirstMessageToDeviceSend(unittest.TestCase):
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
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_first_message(self):
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id,
            "text_message": "Salut mamie"
        }
        response = self.api.post('/message/device/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.circle.conversations) == 1
        assert self.circle.conversations[0].device_access == True
        assert self.circle.conversations[0].name == "Mamie"
        assert self.circle.conversations[0].messages[0].text_content == "Salut mamie"

    def test_invalid_circle_id(self):
        json_data = {
            "token": self.token1,
            "circle_id": 200000,
            "text_message": "Salut mamie"
        }
        response = self.api.post('/message/device/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "token": self.tokenAdmin,
            "circle_id": self.circle.id,
            "text_message": "Salut mamie"
        }
        response = self.api.post('/message/device/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1,
            "text_message": "Salut mamie"
        }
        response = self.api.post('/message/device/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestFirstMessageSend(unittest.TestCase):
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
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_message_send(self):
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id,
            "email": self.user2.email,
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.circle.conversations) == 1
        assert len(self.circle.conversations[0].messages) == 1
        assert self.circle.conversations[0].messages[0].text_content == "Salut frangin"

    def test_invalid_user(self):
        json_data = {
            "token": self.tokenAdmin,
            "circle_id": self.circle.id,
            "email": self.user2.email,
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1,
            "email": self.user2.email,
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_circle(self):
        json_data = {
            "token": self.tokenAdmin,
            "circle_id": 2000000,
            "email": self.user2.email,
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_dest(self):
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id,
            "email": "contact.projetneo@gmail.com",
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/first-message', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False


class TestMessageSend(unittest.TestCase):
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
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation, privilege="STANDARD")
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_message_send(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conversation.id,
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.conversation.messages) == 1
        assert self.conversation.messages[0].text_content == "Salut frangin"

    def test_invalid_user(self):
        json_data = {
            "token": self.tokenAdmin,
            "conversation_id": self.conversation.id,
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 200000,
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1,
            "text_message": "Salut frangin"
        }
        response = self.api.post('/message/send', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False
