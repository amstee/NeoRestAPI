import unittest
import sys
import json
sys.path.insert(0,'..')
from api import neoapi

class AccountCreate(unittest.TestCase):

    def test_valide_request(self):
        neo = neoapi()
        test = neo.activate_testing()
        todo = {
                "email": "test@test.com",
                "last_name": "Last Name",
                "password": "VerySecurePassword",
                "first_name": "First Name",
                "birthday": "1995-12-25"
                }
        vr = test.post('/account/create', data=json.dumps(todo), content_type='application/json')
        print(vr)

    def test_no_json(self):
        neo = neoapi()
        test = neo.activate_testing()
        todo = {
                "email": "test@test.com",
                "last_name": "Last Name",
                "password": "VerySecurePassword",
                "first_name": "First Name",
                "birthday": "1995-12-25"
                }
        vr = test.post('/account/create', data=json.dumps(todo), content_type='application/json')
        print(vr)
