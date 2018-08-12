import unittest
import sys
import json

sys.path.insert(0,'..')
from api import NeoAPI
from routes.Facebook import SendMessage

MESSENGER_ID_TESTING="1726772610739883"

class Messaging(unittest.TestCase):
    def test_invalid_recipient(self):
        response = SendMessage(0000000000000, "unitary test")
        assert response[1] == 400

    def test_valid_recipient(self):
        response = SendMessage(MESSENGER_ID_TESTING, "unitary test")
        assert response[1] == 200

    def test_invalid_message(self):
        response = SendMessage(MESSENGER_ID_TESTING, "")
        assert response[1] == 400

class TokenLink(unittest.TestCase):
    def setUp(self):
        neo = NeoAPI()
        self.api = neo.activate_testing()
    
    def test_invalid_token(self):
        json_data = {
            'object': 'page',
            'entry': [
                {
                    'id': '2084962175122458',
                    'time': 1534077264598,
                    'messaging': [
                        {
                            'sender': {
                                'id': '1726772610739883'
                                },
                            'recipient': {
                                'id': '2084962175122458'
                                },
                            'timestamp': 1534077263855,
                            'message': {
                                'mid': 'BygawGFup0NPZeLqaWMtJfRQ8NlZ8m_HmSH6bWSVfYD4JPg8bqPYop9c2xaoOPGTFIgaRCvNtgFf1Ynpy3K-mQ',
                                'seq': 292,
                                'text': '/token invalid'
                                }
                        }]
                }]
            }
        response = self.api.post('/api/messenger/webhook', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        response_json = json.loads(response_json)
        assert response.status_code == 200
        assert response_json["message"]["text"] == "Token invalide, authentifiez vous a nouveau"

    def test_void_token(self):
        json_data = {
            'object': 'page',
            'entry': [
                {
                    'id': '2084962175122458',
                    'time': 1534077264598,
                    'messaging': [
                        {
                            'sender': {
                                'id': '1726772610739883'
                                },
                            'recipient': {
                                'id': '2084962175122458'
                                },
                            'timestamp': 1534077263855,
                            'message': {
                                'mid': 'BygawGFup0NPZeLqaWMtJfRQ8NlZ8m_HmSH6bWSVfYD4JPg8bqPYop9c2xaoOPGTFIgaRCvNtgFf1Ynpy3K-mQ',
                                'seq': 292,
                                'text': '/token '
                                }
                        }]
                }]
            }
        response = self.api.post('/api/messenger/webhook', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        response_json = json.loads(response_json)
        assert response.status_code == 200
        assert response_json["message"]["text"] == "Token invalide, authentifiez vous a nouveau"

    def test_unliked_account(self):
        json_data = {
            'object': 'page',
            'entry': [
                {
                    'id': '2084962175122458',
                    'time': 1534077264598,
                    'messaging': [
                        {
                            'sender': {
                                'id': '1726772610739883'
                                },
                            'recipient': {
                                'id': '2084962175122458'
                                },
                            'timestamp': 1534077263855,
                            'message': {
                                'mid': 'BygawGFup0NPZeLqaWMtJfRQ8NlZ8m_HmSH6bWSVfYD4JPg8bqPYop9c2xaoOPGTFIgaRCvNtgFf1Ynpy3K-mQ',
                                'seq': 292,
                                'text': 'unitary test'
                                }
                        }]
                }]
            }
        response = self.api.post('/api/messenger/webhook', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        response_json = json.loads(response_json)
        assert response.status_code == 200
        assert response_json["message"]["text"] == "Votre compte messenger n'est lié a aucun compte NEO"