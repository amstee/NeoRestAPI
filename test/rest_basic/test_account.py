import unittest
import json
from config.loader import neo_config
from api import NeoAPI
from config.database import db
from models.User import User as UserModel
from utils.testutils import authenticate_user
from gevent import monkey
monkey.patch_all()


class AccountCreate(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        db.session.query(UserModel).delete()
        db.session.commit()

    def test_valid_request(self):
        json_data = {
            "email": "test@test.com",
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "first_name": "First Name",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 201
        assert response_json['success'] is True

    def test_empty_json(self):
        todo = {}
        response = self.api.post('/account/create', data=json.dumps(todo), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] is False

    def test_missing_email(self):
        json_data = {
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "first_name": "First Name",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] is False

    def test_missing_last_name(self):
        json_data = {
            "email": "test@test.com",
            "password": "VerySecurePassword",
            "first_name": "First Name",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] is False

    def test_missing_password(self):
        json_data = {
            "email": "test@test.com",
            "last_name": "Last Name",
            "first_name": "First Name",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] is False

    def test_missing_first_name(self):
        json_data = {
            "email": "test@test.com",
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] is False

    def test_missing_birthday(self):
        json_data = {
            "email": "test@test.com",
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "first_name": "First Name"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] is False

    def test_unreadable_string_birthday(self):
        json_data = {
            "email": "test@test.com",
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "first_name": "First Name",
            "birthday": "mqksdmlqskdmlqskdqmlsdkqmsd"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 500
        assert response_json['success'] is False

    def test_used_mail(self):
        new_user = UserModel(
            email="clone@gmail.com",
            password="password",
            first_name="first_name",
            last_name="last_name",
            birthday="1999-02-02"
            )
        db.session.add(new_user)
        db.session.commit()
        json_data = {
            "email": "clone@gmail.com",
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "first_name": "First Name",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 409
        assert response_json['success'] is False


class AccountLogin(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        db.session.query(UserModel).delete()
        db.session.commit()

        new_user = UserModel(
            email="clone2@gmail.com",
            password="password",
            first_name="first_name",
            last_name="last_name",
            birthday="1999-02-02"
            )
        db.session.add(new_user)
        db.session.commit()

    def test_valid_request(self):
        json_data = {
            "email": "clone2@gmail.com",
            "password": "password"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True

    def test_missing_email(self):
        json_data = {
            "password": "password"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] is False

    def test_missing_password(self):
        json_data = {
            "email": "clone2@gmail.com"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] is False

    def test_wrong_password(self):
        json_data = {
            "email": "clone2@gmail.com",
            "password": "passwordWrong"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 401
        assert response_json['success'] is False

    def test_double_login(self):
        json_data = {
            "email": "clone2@gmail.com",
            "password": "password"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True


class AccountApiToken(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testcircle@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testcircle@test.com", password="test", first_name="firstname",
                                   last_name="lastname", birthday="1995-12-12")
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")

    def test_valid_token(self):
        json_data = {
            "token": self.token1,
        }
        response = self.api.post('/token/verify', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] is True

    def test_invalid_token(self):
        json_data = {
            "token": "tetetetet",
        }
        response = self.api.post('/token/verify', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 401
        assert response_json['success'] is False
