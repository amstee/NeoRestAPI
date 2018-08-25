import unittest
import sys
import json

sys.path.insert(0,'..')
from config.loader import neo_config
from api import NeoAPI
from config.database import db
from models.User import User as UserModel
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from utils.testutils import authenticate_user


class TestCircleCreate(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcircle@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcircle@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcircle2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcircle2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")

    def test_valid_request(self):
        json_data = {
            "name": "CircleCreationTest",
            "token": self.token1
        }
        response = self.api.post('/circle/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert response_json['content']["name"] == "CircleCreationTest"

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/circle/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] is False


class TestCircleDelete(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcircledelete@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcircledelete@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcircledelete2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcircledelete2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_circle(self):
        self.circle = Circle("TESTDELETION")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db.session.commit()

    def test_valid_deletion(self):
        id = self.circle.id
        json_data = {
            "token": self.tokenAdmin,
            "circle_id": self.circle.id
        }
        response = self.api.post('/admin/circle/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        c = db.session.query(Circle).filter(Circle.id==id).first()
        assert c == None

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "circle_id": self.circle.id
        }
        response = self.api.post('/admin/circle/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.tokenAdmin
        }
        response = self.api.post('/admin/circle/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_circle(self):
        json_data = {
            "token": self.tokenAdmin,
            "circle_id": 20000000
        }
        response = self.api.post('/admin/circle/delete', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False


class TestCircleUpdate(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcircleupdate@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcircleupdate@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcircleupdate2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcircleupdate2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_circle(self):
        self.circle = Circle("TESTUPDATE")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db.session.commit()

    def test_valid_update(self):
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id,
            "name": "UPDATED"
        }
        response = self.api.post('/circle/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert self.circle.name == "UPDATED"

    def test_empty_update(self):
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id,
        }
        response = self.api.post('/circle/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert self.circle.name != "UPDATED"

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1,
        }
        response = self.api.post('/circle/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "circle_id": self.circle.id,
            "name": "UPDATED"
        }
        response = self.api.post('/circle/update', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False


class TestCircleInfo(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcircleinfo@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcircleinfo@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcircleinfo2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcircleinfo2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_circle(self):
        self.circle = Circle("TESTUPDATE")
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db.session.commit()

    def test_valid_info(self):
        json_data = {
            "token": self.token1,
            "circle_id": self.circle.id,
        }
        response = self.api.post('/circle/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert self.circle.name == response_json["content"]["name"]

    def test_invalid_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/circle/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_invalid_user(self):
        json_data = {
            "token": self.token2,
            "circle_id": self.circle.id,
        }
        response = self.api.post('/circle/info', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 403
        assert response_json['success'] == False


class TestCircleList(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcirclelist@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcirclelist@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testcirclelist2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testcirclelist2@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1111-11-11")
        self.create_circle("INFO1")
        self.create_circle("INFO2")
        self.create_circle("INFO3")
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")
        self.tokenAdmin = authenticate_user(self.api, "contact.projetneo@gmail.com", "PapieNeo2019")

    def create_circle(self, name):
        self.circle = Circle(name)
        self.link = UserToCircle()
        self.link.user = self.user1
        self.link.circle = self.circle
        db.session.commit()

    def test_valid_list(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/circle/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert response_json['content'][0]["name"] == "INFO1"
        assert response_json['content'][1]["name"] == "INFO2"
        assert response_json['content'][2]["name"] == "INFO3"


    def test_empty_list(self):
        json_data = {
            "token": self.token2
        }
        response = self.api.post('/circle/list', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True
        assert len(response_json["content"]) == 0

