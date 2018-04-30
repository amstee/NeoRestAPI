import unittest
import sys
import json

sys.path.insert(0,'..')
from api import neoapi
from config.database import db_session
from models.User import User as UserModel

class TestFirstDeviceMessageSend(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()

class TestDeviceMessageSend(unittest.TestCase):
    def setUp(self):
        neo = neoapi()
        self.api = neo.activate_testing()
        db_session.query(UserModel).delete()
        db_session.commit()