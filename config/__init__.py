from flask import Flask
from flask_session import Session
from flask_restful import Api
from flask_cors import CORS
from flask_socketio import SocketIO
from routes import ResourceManager
from models.User import User
from .sockets import sockets
from .redis import RedisSessionInterface
from utils.database import init_default_content, clean_default_content
from .database import URI_USED, init_db
# import redis

socketio = SocketIO(async_mode="gevent")


class NeoAPI(object):
    def __init__(self, config):
        self.config = config
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = URI_USED
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config['SECRET_KEY'] = config.neo_secret
        self.app.config["SESSION_TYPE"] = "null"
        from sockets import sockets as socket_blueprint
        self.app.register_blueprint(socket_blueprint)

        self.session = Session()
        self.app.session_interface = RedisSessionInterface()
        self.session.init_app(self.app)

        self.api = Api(self.app)
        CORS(self.app)

        ResourceManager.add_account_resources(self.api)
        ResourceManager.add_device_routes(self.api)
        ResourceManager.add_api_resources(self.api)
        ResourceManager.add_cookies_resources(self.api)
        ResourceManager.add_payment_resources(self.api)
        ResourceManager.add_circle_logic_resources(self.api)
        ResourceManager.add_circle_resources(self.api)
        ResourceManager.add_conversation_logic_resources(self.api)
        ResourceManager.add_conversation_resources(self.api)
        ResourceManager.add_media_resources(self.api)
        ResourceManager.add_media_logic_resources(self.api)
        ResourceManager.add_message_resources(self.api)
        ResourceManager.add_user_message_resources(self.api)
        ResourceManager.add_device_message_resources(self.api)

        socketio.init_app(self.app)
        init_db(self.app)

    def activate_testing(self):
        self.app.config['TESTING'] = True
        self.app.app_context().push()
        User.CreateNeoAdmin(self.config.admin_password)
        init_default_content(self.config.beta_user1_password, self.config.beta_user2_password)
        return self.app.test_client()


def create_app(config):
    neo = NeoAPI(config)
    if config.use_redis:
        sockets.storage.set_conf(config.use_redis, config.redis_url)
    with neo.app.app_context():
        User.CreateNeoAdmin(config.admin_password)
        init_default_content(config.beta_user1_password, config.beta_user2_password)
    return neo.app
