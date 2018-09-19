from api import NeoAPI
import unittest
from config.loader import neo_config
from utils import database as db_utils
from utils import testutils
from classes.RedisStorage import RedisStorage
from config.sockets import sockets
from sockets.socket_core import authentication_events as ae


class SocketClientsStorage(unittest.TestCase):
    def setUp(self):
        neo_config.load_config()
        neo_config.set_project_variables()
        self.neo = NeoAPI(neo_config)
        self.api = self.neo.activate_testing()
        self.u1 = db_utils.get_user("user1.beta@test.com")
        self.u2 = db_utils.get_user("user2.beta@test.com")
        self.t1 = testutils.authenticate_user(self.api, self.u1, neo_config.beta_user1_password)
        self.t2 = testutils.authenticate_user(self.api, self.u2, neo_config.beta_user2_password)
        self.use_redis = neo_config.use_redis
        self.url = neo_config.redis_url_dev
        if self.use_redis:
            sockets.storage.set_conf(self.use_redis, self.url)
            self.redis_conn = sockets.storage
            RedisStorage.clean_databases(self.url)

    def tearDown(self):
        db_utils.clean_default_content()
        RedisStorage.clean_databases(self.url)

    def test_create_client(self):
        ae.authentication(self.t1, "test_session_id")
        assert len(sockets) == 1
        ae.authentication(self.t2, "test_session_id2")
        assert len(sockets) == 2
        ae.disconnection("test_session_id")
        assert len(sockets) == 1
        ae.disconnection("test_session_id2")
        assert len(sockets) == 0
