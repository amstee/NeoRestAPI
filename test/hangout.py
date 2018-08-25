import unittest
import sys
import json

sys.path.insert(0,'..')
from config.loader import neo_config
from api import NeoAPI
from bot.hangout import send_to_space

TESTING_SPACE="spaces/v4YQNAAAAAE"


class Messaging(unittest.TestCase):
    def test_message_valid_space(self):
        response = send_to_space(TESTING_SPACE, "unitary test")
        assert response['text'] == "unitary test"

    def test_message_invalid_space(self):
        try:
            send_to_space("spaces/----", "unitary test")
        except Exception as ex:
            assert "Error received" == "Error received"
    
    def test_invalid_message(self):
        try:
            send_to_space(TESTING_SPACE, "")
        except Exception as ex:
            assert "Error received" == "Error received"


class TokenLink(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        neo = NeoAPI(neo_config)
        self.api = neo.activate_testing()

    def test_invalid_token(self):
        json_data = {
            'type': 'MESSAGE',
            'eventTime': '2018-07-20T22:42:11.139359Z',
            'token': 'yZZieXB8D64T1qMxI9fJVCgC1vVMUB70PB9p3lIYSN4=',
            'message': {
                'name': 'spaces/v4YQNAAAAAE/messages/mQK8ze_uheQ.mQK8ze_uheQ',
                'sender': {
                    'name': 'users/110936718053534267233',
                    'displayName': 'Paul-Sirawit Kerebel',
                    'avatarUrl': 'https://lh3.googleusercontent.com/-Pqpjwgvt0ho/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7ptADXkPo'
                                 'NldHy6z8kq7gUKOjeJNw/mo/photo.jpg',
                    'email': 'paul.kerebel@api.neo.ovh',
                    'type': 'HUMAN'
                    },
                'createTime': '2018-07-20T22:42:11.139359Z',
                'text': '/token invalidtoken',
                'thread': {
                    'name': 'spaces/v4YQNAAAAAE/threads/mQK8ze_uheQ',
                    'retentionSettings': {
                        'state': 'PERMANENT'
                        }
                    },
                'space': {
                    'name': 'spaces/v4YQNAAAAAE',
                    'type': 'DM'
                    },
                'argumentText': 'test'
                },
            'user': {
                'name': 'users/110936718053534267233',
                'displayName': 'Paul-Sirawit Kerebel',
                'avatarUrl': 'https://lh3.googleusercontent.com/-Pqpjwgvt0ho/AAAAAAAAAAI/AAAAAAAAAAA'
                             '/AAnnY7ptADXkPoNldHy6z8kq7gUKOjeJNw/mo/photo.jpg',
                'email': 'paul.kerebel@api.neo.ovh',
                'type': 'HUMAN'
                },
            'space': {
                'name': 'spaces/v4YQNAAAAAE',
                'type': 'DM'
                },
            'configCompleteRedirectUrl': 'https://chat.google.com/api/bot_config_complete?token=AI8PGBaeEDhoPgLv9v6ltym'
                                         '1tAB6wum7HRSLk3dZrIkFKCnJyCDt-hVZoA9NgXoeWtdpgu_CyoSmuCL11Sl7uranPehaBsBXKGCv'
                                         'N6uhJHMBPHHcIY3MjqTeClYDzumPS6LH2Qwdmkv5IJ1-ymbR'
            }
        response = self.api.post('/api/hangout/webhook', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['text'] == 'Token invalide, authentifiez vous a nouveau'

    def test_void_token(self):
        json_data = {
            'type': 'MESSAGE',
            'eventTime': '2018-07-20T22:42:11.139359Z',
            'token': 'yZZieXB8D64T1qMxI9fJVCgC1vVMUB70PB9p3lIYSN4=',
            'message': {
                'name': 'spaces/v4YQNAAAAAE/messages/mQK8ze_uheQ.mQK8ze_uheQ',
                'sender': {
                    'name': 'users/110936718053534267233',
                    'displayName': 'Paul-Sirawit Kerebel',
                    'avatarUrl': 'https://lh3.googleusercontent.com/-Pqpjwgvt0ho/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7ptADXkPo'
                                 'NldHy6z8kq7gUKOjeJNw/mo/photo.jpg',
                    'email': 'paul.kerebel@api.neo.ovh',
                    'type': 'HUMAN'
                    },
                'createTime': '2018-07-20T22:42:11.139359Z',
                'text': '/token ',
                'thread': {
                    'name': 'spaces/v4YQNAAAAAE/threads/mQK8ze_uheQ',
                    'retentionSettings': {
                        'state': 'PERMANENT'
                        }
                    },
                'space': {
                    'name': 'spaces/v4YQNAAAAAE',
                    'type': 'DM'
                    },
                'argumentText': 'test'
                },
            'user': {
                'name': 'users/110936718053534267233',
                'displayName': 'Paul-Sirawit Kerebel',
                'avatarUrl': 'https://lh3.googleusercontent.com/-Pqpjwgvt0ho/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7ptADXkPoNldH'
                             'y6z8kq7gUKOjeJNw/mo/photo.jpg',
                'email': 'paul.kerebel@api.neo.ovh',
                'type': 'HUMAN'
                },
            'space': {
                'name': 'spaces/v4YQNAAAAAE',
                'type': 'DM'
                },
            'configCompleteRedirectUrl': 'https://chat.google.com/api/bot_config_complete?token=AI8PGBaeEDhoPgLv9v6ltym'
                                         '1tAB6wum7HRSLk3dZrIkFKCnJyCDt-hVZoA9NgXoeWtdpgu_CyoSmuCL11Sl7uranPehaBsBXKGCv'
                                         'N6uhJHMBPHHcIY3MjqTeClYDzumPS6LH2Qwdmkv5IJ1-ymbR'
            }
        response = self.api.post('/api/hangout/webhook', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['text'] == 'Token invalide, authentifiez vous a nouveau'

    def test_unlinked_account(self):
        json_data = {
            'type': 'MESSAGE',
            'eventTime': '2018-07-20T22:42:11.139359Z',
            'token': 'yZZieXB8D64T1qMxI9fJVCgC1vVMUB70PB9p3lIYSN4=',
            'message': {
                'name': 'spaces/v4YQNAAAAAE/messages/mQK8ze_uheQ.mQK8ze_uheQ',
                'sender': {
                    'name': 'users/110936718053534267233',
                    'displayName': 'Paul-Sirawit Kerebel',
                    'avatarUrl': 'https://lh3.googleusercontent.com/-Pqpjwgvt0ho/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7ptADXkPo'
                                 'NldHy6z8kq7gUKOjeJNw/mo/photo.jpg',
                    'email': 'paul.kerebel@api.neo.ovh',
                    'type': 'HUMAN'
                    },
                'createTime': '2018-07-20T22:42:11.139359Z',
                'text': 'text unlinked account',
                'thread': {
                    'name': 'spaces/v4YQNAAAAAE/threads/mQK8ze_uheQ',
                    'retentionSettings': {
                        'state': 'PERMANENT'
                        }
                    },
                'space': {
                    'name': 'spaces/v4YQNAAAAAE',
                    'type': 'DM'
                    },
                'argumentText': 'test'
                },
            'user': {
                'name': 'users/110936718053534267233',
                'displayName': 'Paul-Sirawit Kerebel',
                'avatarUrl': 'https://lh3.googleusercontent.com/-Pqpjwgvt0ho/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7ptADXkPoNldH'
                             'y6z8kq7gUKOjeJNw/mo/photo.jpg',
                'email': 'paul.kerebel@api.neo.ovh',
                'type': 'HUMAN'
                },
            'space': {
                'name': 'spaces/v4YQNAAAAAE',
                'type': 'DM'
                },
            'configCompleteRedirectUrl': 'https://chat.google.com/api/bot_config_complete?token=AI8PGBaeEDhoPgLv9v6ltym'
                                         '1tAB6wum7HRSLk3dZrIkFKCnJyCDt-hVZoA9NgXoeWtdpgu_CyoSmuCL11Sl7uranPehaBsBXKGCv'
                                         'N6uhJHMBPHHcIY3MjqTeClYDzumPS6LH2Qwdmkv5IJ1-ymbR'
            }
        response = self.api.post('/api/hangout/webhook', data=json.dumps(json_data), content_type='application/json')
        response_json = json.loads(response.data)
        assert response.status_code == 200
        assert response_json['text'] == "Votre compte hangout n'est lié a aucun compte NEO"

