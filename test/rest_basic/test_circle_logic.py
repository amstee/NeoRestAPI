import unittest
import json
from config.loader import neo_config
from api import NeoAPI
from config.database import db
from models.User import User as UserModel
from models.UserToCircle import UserToCircle
from models.CircleInvite import CircleInvite
from models.Circle import Circle
from utils.testutils import authenticate_user
from core import circle_logic
from gevent import monkey
monkey.patch_all()


class TestCircleInvite(unittest.TestCase):
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
        self.circle = Circle(name="TestCircleInvite")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
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
            "circle_id": self.circle.id,
            "email": self.user2.email
        }
        response = self.api.post('/circle/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success']

    def test_missing_circle_id(self):
        json_data = {
            "token": self.token1,
            "email": self.user2.email
        }
        response = self.api.post('/circle/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_missing_email(self):
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id
        }
        response = self.api.post('/circle/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_circle(self):
        json_data = {
            "token": self.token1,
            "circle_id": 2000000,
            "email": self.user2.email
        }
        response = self.api.post('/circle/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_email(self):
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id,
            "email": "invalid.email@email.com"
        }
        response = self.api.post('/circle/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_user(self):
        json_data = {
            "token": self.token3,
            "circle_id": self.circle.id,
            "email": self.user2.email
        }
        response = self.api.post('/circle/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert not response_json['success']

    def test_already_existing_user(self):
        json_data = {
            "token": self.token3,
            "circle_id": self.circle.id,
            "email": self.user2.email
        }
        circle_logic.invite(self.circle.id, self.user2.email, self.user3, False)
        response = self.api.post('/circle/invite', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']


class TestCircleJoin(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclejoin@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclejoin@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclejoin2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclejoin2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="TestCircleJoin")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.invite = CircleInvite()
        self.invite.user = self.user2
        self.invite.circle = self.circle
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.delete(self.circle)
        db.session.commit()

    def test_valid_join(self):
        json_data = {
            "token": self.token2,
            "invite_id": self.invite.id
        }
        response = self.api.post('/circle/join', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success']

    def test_missing_parameter(self):
        json_data = {
            "token": self.token2
        }
        response = self.api.post('/circle/join', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_invite_id(self):
        json_data = {
            "token": self.token2,
            "invite_id": 2000000
        }
        response = self.api.post('/circle/join', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_user(self):
        json_data = {
            "token": self.token1,
            "invite_id": self.invite.id
        }
        response = self.api.post('/circle/join', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert not response_json['success']


class TestCircleReject(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclereject@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclereject@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclereject2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclereject2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.circle = Circle(name="TestCircleReject")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.invite = CircleInvite()
        self.invite.user = self.user2
        self.invite.circle = self.circle
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.delete(self.circle)
        db.session.commit()

    def test_valid_reject(self):
        json_data = {
            "token": self.token2,
            "invite_id": self.invite.id
        }
        response = self.api.post('/circle/reject', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        deleted_invite = db.session.query(CircleInvite).filter_by(user_id=self.user2.id,
                                                                  circle_id=self.circle.id).first()
        assert deleted_invite is None
        assert response.status_code == 200
        assert response_json['success']

    def test_missing_parameter(self):
        json_data = {
            "token": self.token2
        }
        response = self.api.post('/circle/reject', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_invalid_user(self):
        json_data = {
            "token": self.token1,
            "invite_id": self.invite.id
        }
        response = self.api.post('/circle/reject', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert not response_json['success']

    def test_invalid_invite_id(self):
        json_data = {
            "token": self.token2,
            "invite_id": 2000000
        }
        response = self.api.post('/circle/reject', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']


class TestCircleQuit(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclequit@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclequit@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclequit2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclequit2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testcirclequit3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testcirclequit3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.circle = Circle(name="TestCircleReject")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.invite = CircleInvite()
        self.invite.user = self.user2
        self.invite.circle = self.circle
        self.link1 = UserToCircle()
        self.link1.user = self.user3
        self.link1.circle = self.circle
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
        json_data = {
            "token": self.token3,
            "circle_id": self.circle.id
        }
        response = self.api.post('/circle/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success']

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "circle_id": self.circle.id
        }
        response = self.api.post('/circle/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert not response_json['success']

    def test_missing_parameter(self):
        json_data = {
            "token": self.token3
        }
        response = self.api.post('/circle/quit', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert not response_json['success']

    def test_all_user_quit(self):
        circle_id = self.circle.id
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id
        }
        response1 = self.api.post('/circle/quit', data=json.dumps(json_data), content_type='application/json')
        response_json1 = json.loads(response1.data)
        json_data_2 = {
            "token": self.token3,
            "circle_id": self.circle.id
        }
        response2 = self.api.post('/circle/quit', data=json.dumps(json_data_2), content_type='application/json')
        response_json2 = json.loads(response2.data)
        assert response1.status_code == 200
        assert response_json2['success'] is True
        assert response1.status_code == 200
        assert response_json1['success'] is True
        c = db.session.query(Circle).filter(Circle.id == circle_id).first()
        assert c is None


class TestCircleKick(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclequit@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclequit@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclequit2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclequit2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.user3 = db.session.query(UserModel).filter(UserModel.email == "testcirclequit3@test.com").first()
        if self.user3 is None:
            self.user3 = UserModel(email="testcirclequit3@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.circle = Circle(name="TestCircleReject")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        self.invite = CircleInvite()
        self.invite.user = self.user2
        self.invite.circle = self.circle
        self.link1 = UserToCircle()
        self.link1.user = self.user3
        self.link1.circle = self.circle
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
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id,
            "email": self.user3.email
        }
        response = self.api.post('/circle/kick', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
