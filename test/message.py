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
from models.Message import Message
from utils.testutils import authenticate_user


class TestMessageCreate(unittest.TestCase):
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
        self.circle = Circle(name="TestMessageCreate")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle, name="TestMessageCreate")
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation)
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_message(self):
        json_data = {
            "token": self.tokenAdmin,
            "files": [],
            "link_id": self.linkConversation.id,
            "text": "Default Test Message",
            "directory_name": "Tests"
        }
        response = self.api.post('/admin/message/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.linkConversation.messages) == 1
        assert len(self.conversation.messages) == 1

    def test_invalid_link(self):
        json_data = {
            "token": self.tokenAdmin,
            "files": [],
            "link_id": 200000,
            "text": "Default Test Message",
            "directory_name": "Tests"
        }
        response = self.api.post('/admin/message/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "token": self.token1,
            "files": [],
            "link_id": self.linkConversation.id,
            "text": "Default Test Message",
            "directory_name": "Tests"
        }
        response = self.api.post('/admin/message/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1,
            "files": [],
            "text": "Default Test Message",
            "directory_name": "Tests"
        }
        response = self.api.post('/admin/message/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestMessageDelete(unittest.TestCase):
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
        self.circle = Circle(name="TestMessageCreate")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle, name="TestMessageCreate")
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation)
        self.message = Message(link=self.linkConversation, conversation=self.conversation,
                               content="1")
        self.message2 = Message(link=self.linkConversation, conversation=self.conversation,
                               content="2")
        self.message3 = Message(link=self.linkConversation2, conversation=self.conversation,
                               content="3")
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_deletion(self):
        json_data = {
            "token": self.token1,
            "message_id": self.message2.id
        }
        response = self.api.post('/message/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(self.linkConversation.messages) == 1
        assert len(self.conversation.messages) == 2
        assert self.linkConversation.messages[0].text_content == "1"

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "message_id": self.message2.id
        }
        response = self.api.post('/message/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/message/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_message(self):
        json_data = {
            "token": self.token1,
            "message_id": 200000
        }
        response = self.api.post('/message/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestMessageInfo(unittest.TestCase):
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
        self.circle = Circle(name="TestMessageCreate")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle, name="TestMessageCreate")
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation)
        self.message = Message(link=self.linkConversation, conversation=self.conversation,
                               content="1")
        self.message2 = Message(link=self.linkConversation, conversation=self.conversation,
                               content="2")
        self.message3 = Message(link=self.linkConversation2, conversation=self.conversation,
                               content="3")
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_info(self):
        json_data = {
            "token": self.token1,
            "message_id": self.message2.id
        }
        response = self.api.post('/message/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert response_json["content"]["content"] == "2"

    def test_valid_info2(self):
        json_data = {
            "token": self.token2,
            "message_id": self.message.id
        }
        response = self.api.post('/message/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert response_json["content"]["content"] == "1"

    def test_invalid_user(self):
        json_data = {
            "token": self.tokenAdmin,
            "message_id": self.message2.id
        }
        response = self.api.post('/message/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/message/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_message(self):
        json_data = {
            "token": self.token1,
            "message_id": 200000
        }
        response = self.api.post('/message/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestMessageList(unittest.TestCase):
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
        self.circle = Circle(name="TestMessageCreate")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle, name="TestMessageCreate")
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation)
        self.message = Message(link=self.linkConversation, conversation=self.conversation,
                               content="1")
        self.message2 = Message(link=self.linkConversation, conversation=self.conversation,
                               content="2")
        self.message3 = Message(link=self.linkConversation2, conversation=self.conversation,
                               content="3")
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_list(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conversation.id,
            "quantity": 100
        }
        response = self.api.post('/conversation/message/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(response_json["content"]) == 3
        assert response_json["content"][0]["content"] == "1"
        assert response_json["content"][1]["content"] == "2"
        assert response_json["content"][2]["content"] == "3"

    def test_small_quantity(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conversation.id,
            "quantity": 2
        }
        response = self.api.post('/conversation/message/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(response_json["content"]) == 2
        assert response_json["content"][0]["content"] == "1"
        assert response_json["content"][1]["content"] == "2"

    def test_invalid_quantity(self):
        json_data = {
            "token": self.token1,
            "conversation_id": self.conversation.id,
            "quantity": 0
        }
        response = self.api.post('/conversation/message/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1,
            "quantity": 100
        }
        response = self.api.post('/conversation/message/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "token": self.tokenAdmin,
            "conversation_id": self.conversation.id,
            "quantity": 100
        }
        response = self.api.post('/conversation/message/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_invalid_conversation(self):
        json_data = {
            "token": self.token1,
            "conversation_id": 2000000,
            "quantity": 100
        }
        response = self.api.post('/conversation/message/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestMessageUpdate(unittest.TestCase):
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
        self.circle = Circle(name="TestMessageCreate")
        self.linkCircle = UserToCircle(user=self.user1, circle=self.circle)
        self.linkCircle2 = UserToCircle(user=self.user2, circle=self.circle)
        self.conversation = Conversation(circle=self.circle, name="TestMessageCreate")
        self.linkConversation = UserToConversation(user=self.user1, conversation=self.conversation, privilege="ADMIN")
        self.linkConversation2 = UserToConversation(user=self.user2, conversation=self.conversation)
        self.message = Message(link=self.linkConversation, conversation=self.conversation,
                               content="1")
        self.message2 = Message(link=self.linkConversation, conversation=self.conversation,
                               content="2")
        self.message3 = Message(link=self.linkConversation2, conversation=self.conversation,
                               content="3")
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def test_valid_update(self):
        json_data = {
            "token": self.token1,
            "message_id": self.message.id,
            "text_content": "4"
        }
        response = self.api.post('/message/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert self.message.text_content == "4"

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1,
            "message_id": self.message.id
        }
        response = self.api.post('/message/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "message_id": self.message.id,
            "text_content": "4"
        }
        response = self.api.post('/message/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_invalid_message(self):
        json_data = {
            "token": self.token1,
            "message_id": 2000000,
            "text_content": "4"
        }
        response = self.api.post('/message/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False
