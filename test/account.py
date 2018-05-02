import unittest
import sys
import json

sys.path.insert(0,'..')
from api import neoapi
from config.database import db_session
from models.User import User as UserModel

class AccountCreate(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

    def test_valide_request(self):
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
        assert response_json['success'] == True

    def test_empty_json(self):
        todo = {}
        response = self.api.post('/account/create', data=json.dumps(todo), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 409
        assert response_json['success'] == False

    def test_missing_email(self):
        json_data = {
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "first_name": "First Name",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 409
        assert response_json['success'] == False

    def test_missing_last_name(self):
        json_data = {
            "email": "test@test.com",
            "password": "VerySecurePassword",
            "first_name": "First Name",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 409
        assert response_json['success'] == False

    def test_missing_password(self):
        json_data = {
            "email": "test@test.com",
            "last_name": "Last Name",
            "first_name": "First Name",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 409
        assert response_json['success'] == False

    def test_missing_first_name(self):
        json_data = {
            "email": "test@test.com",
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "birthday": "1995-12-25"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 409
        assert response_json['success'] == False

    def test_missing_birthday(self):
        json_data = {
            "email": "test@test.com",
            "last_name": "Last Name",
            "password": "VerySecurePassword",
            "first_name": "First Name"
        }
        response = self.api.post('/account/create', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 409
        assert response_json['success'] == False

    def test_used_mail(self):
        new_user = UserModel(
            email="clone@gmail.com",
            password="password",
            first_name="first_name",
            last_name="last_name",
            birthday="1999-02-02"
            )
        db_session.add(new_user)
        db_session.commit()
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
        assert response_json['success'] == False

class AccountLogin(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

        new_user = UserModel(
            email="clone2@gmail.com",
            password="password",
            first_name="first_name",
            last_name="last_name",
            birthday="1999-02-02"
            )
        db_session.add(new_user)
        db_session.commit()

    def test_valide_request(self):
        json_data = {
            "email": "clone2@gmail.com",
            "password": "password"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True

    def test_missing_email(self):
        json_data = {
            "password": "password"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] == False

    def test_missing_password(self):
        json_data = {
            "email": "clone2@gmail.com"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 400
        assert response_json['success'] == False

    def test_wrong_password(self):
        json_data = {
            "email": "clone2@gmail.com",
            "password": "passwordWrong"
        }
        response = self.api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 401
        assert response_json['success'] == False

class AccountInfo(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

        new_user = UserModel(
            email="clone2@gmail.com",
            password="password",
            first_name="first_name",
            last_name="last_name",
            birthday="1999-02-02"
            )
        db_session.add(new_user)
        db_session.commit()