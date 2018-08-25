import unittest
import sys
import json

sys.path.insert(0,'..')
from api import NeoAPI
from config.loader import neo_config
from config.database import db
from utils.testutils import authenticate_user
from models.User import User as UserModel
from models.Circle import Circle
from models.UserToCircle import UserToCircle


class TestFakePayment(unittest.TestCase):
    user1 = None
    circle1 = None
    link1 = None
    token1 = None
    token2 = None

    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()
        self.user1 = db.session.query(UserModel).filter(UserModel.email == "testpayment@test.com").first()
        if self.user1 is None:
            self.user1 = UserModel(email="testpayment@test.com", password="test", first_name="firstname", last_name="lastname", birthday="1995-12-12")
        self.user2 = db.session.query(UserModel).filter(UserModel.email == "testpayment2@test.com").first()
        if self.user2 is None:
            self.user2 = UserModel(email="testpayment2@test.com", password="test", first_name="firstname", last_name="lastname", birthday="1111-11-11")
        self.circle1 = Circle(name="TestPaymentCircle")
        self.link1 =  UserToCircle()
        self.link1.user = self.user1
        self.link1.circle = self.circle1
        db.session.commit()
        self.token1 = authenticate_user(self.api, self.user1, "test")
        self.token2 = authenticate_user(self.api, self.user2, "test")

    def test_valid_request(self):
        json_data = {
            "circle_id": self.circle1.id,
            "token": self.token1
        }
        response = self.api.post('/device/buy', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['success'] == True

    def test_invalid_user(self):
        json_data = {
            "circle_id": self.circle1.id,
            "token": self.token2
        }
        response = self.api.post('/device/buy', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False

    def test_missing_parameter(self):
        json_data = {
            "token": self.token1
        }
        response = self.api.post('/device/buy', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json["success"] == False


    def test_invalid_circle(self):
        json_data = {
            "circle_id": self.circle1.id,
            "token": self.token2
        }
        response = self.api.post('/device/buy', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code != 200
        assert response_json['success'] == False