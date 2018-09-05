from flask import Flask
from flask_session import Session
from flask_restful import Api
from flask_cors import CORS
from flask_socketio import SocketIO
from models.User import User
from .sockets import sockets
from .redis import RedisSessionInterface
import routes.Account as AccountManager
import routes.Device as DeviceManager
import routes.Circle as CircleManager
import routes.CircleLogic as CircleLogicManager
import routes.Payment as PaymentManager
import routes.Message as BasicMessageManager
import routes.MessageLogic as MessageLogicManager
import routes.Media as MediaManager
import routes.Cookies as CookieManager
import routes.MediaLogic as MediaLogicManager
import routes.DeviceMessage as DeviceMessageManager
import routes.ConversationLogic as ConversationLogicManager
import routes.Conversation as ConversationManager
import routes.DeviceMessageLogic as DeviceMessageLogicManager
import routes.Facebook as Facebook
import routes.Hangout as Hangout
from utils.database import init_default_content
from .database import URI_USED, init_db
import redis

socketio = SocketIO(async_mode="gevent")


class NeoAPI(object):
    def __init__(self, config):
        self.config = config
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = URI_USED
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config['SECRET_KEY'] = config.neo_secret
        if config.use_redis:
            self.app.config['SESSION_TYPE'] = "redis"
            self.app.config['SESSION_REDIS'] = redis.from_url(config.redis_url)
        else:
            self.app.config["SESSION_TYPE"] = "null"
        from sockets import sockets as socket_blueprint
        self.app.register_blueprint(socket_blueprint)

        self.session = Session()
        self.app.session_interface = RedisSessionInterface()
        self.session.init_app(self.app)

        self.api = Api(self.app)
        CORS(self.app)

        # ACCOUNT ROUTES
        self.api.add_resource(AccountManager.AccountCreate, '/account/create')
        self.api.add_resource(AccountManager.AccountLogin, '/account/login')
        self.api.add_resource(AccountManager.AccountLogout, '/account/logout')
        self.api.add_resource(AccountManager.AccountInfo, '/account/info')
        self.api.add_resource(AccountManager.AccountModify, '/account/modify')
        self.api.add_resource(AccountManager.MailAvailability, '/email/available')
        self.api.add_resource(AccountManager.ModifyPassword, '/account/modify/password')
        self.api.add_resource(AccountManager.CheckToken, '/token/verify')
        self.api.add_resource(AccountManager.PromoteAdmin, '/admin/account/promote')
        self.api.add_resource(AccountManager.UserInfo, '/device/account/info')
        self.api.add_resource(AccountManager.GetUserInfo, '/user/info/<user_id>')
        self.api.add_resource(AccountManager.GetMailAvailability, '/email/available/<email>')
        # CIRCLE LOGIC ROUTES
        self.api.add_resource(CircleLogicManager.CircleInvite, '/circle/invite')
        self.api.add_resource(CircleLogicManager.CircleJoin, '/circle/join')
        self.api.add_resource(CircleLogicManager.CircleReject, '/circle/reject')
        self.api.add_resource(CircleLogicManager.CircleQuit, '/circle/quit')
        self.api.add_resource(CircleLogicManager.CircleKick, '/circle/kick')
        # Cookies
        self.api.add_resource(CookieManager.SetCookies, "/cookies/set/token")
        # CIRCLE BASIC ROUTES
        self.api.add_resource(CircleManager.CircleCreate, '/circle/create')
        self.api.add_resource(CircleManager.CircleUpdate, '/circle/update')
        self.api.add_resource(CircleManager.CircleDelete, '/admin/circle/delete')
        self.api.add_resource(CircleManager.CircleInfo, '/circle/info')
        self.api.add_resource(CircleManager.CircleList, '/circle/list')
        self.api.add_resource(CircleManager.CircleDeviceInfo, '/device/circle/info')
        # CONVERSATION BASIC ROUTES
        self.api.add_resource(ConversationManager.ConversationCreate, '/admin/conversation/create')
        self.api.add_resource(ConversationManager.ConversationDelete, '/admin/conversation/delete')
        self.api.add_resource(ConversationManager.ConversationDeviceInfo, '/device/conversation/info')
        self.api.add_resource(ConversationManager.ConversationInfo, '/conversation/info')
        self.api.add_resource(ConversationManager.ConversationUpdate, '/conversation/update')
        self.api.add_resource(ConversationManager.ConversationList, '/conversation/list')
        self.api.add_resource(ConversationManager.ConversationDeviceList, '/device/conversation/list')
        # CONVERSATION LOGIC ROUTES
        self.api.add_resource(ConversationLogicManager.ConversationInvite, '/conversation/invite')
        self.api.add_resource(ConversationLogicManager.ConversationKick, '/conversation/kick')
        self.api.add_resource(ConversationLogicManager.ConversationQuit, '/conversation/quit')
        self.api.add_resource(ConversationLogicManager.ConversationRemoveDevice, '/conversation/device/remove')
        self.api.add_resource(ConversationLogicManager.ConversationUserPromote, '/conversation/promote')
        self.api.add_resource(ConversationLogicManager.ConversationAddDevice, '/conversation/device/add')
        # BASIC MESSAGE ROUTES
        self.api.add_resource(BasicMessageManager.MessageCreate, '/admin/message/create')
        self.api.add_resource(BasicMessageManager.MessageDelete, '/message/delete')
        self.api.add_resource(BasicMessageManager.MessageInfo, '/message/info')
        self.api.add_resource(BasicMessageManager.MessageUpdate, '/message/update')
        self.api.add_resource(BasicMessageManager.MessageList, '/conversation/message/list')
        # DEVICE MESSAGE LOGIC MANAGER
        self.api.add_resource(DeviceMessageLogicManager.FirstDeviceMessageSend, '/device/message/first-message')
        self.api.add_resource(DeviceMessageLogicManager.DeviceMessageSend, '/device/message/send')
        # MESSAGE LOGIC ROUTES
        self.api.add_resource(MessageLogicManager.FirstMessageSend, '/message/first-message')
        self.api.add_resource(MessageLogicManager.MessageSend, '/message/send')
        self.api.add_resource(MessageLogicManager.FirstMessageToDeviceSend, '/message/device/first-message')
        # MEDIA LOGIC ROUTES
        self.api.add_resource(MediaLogicManager.DeviceFindMedia, "/device/media/find")
        self.api.add_resource(MediaLogicManager.FindMedia, "/media/find")
        self.api.add_resource(MediaLogicManager.CreateMedia, "/media/create")
        self.api.add_resource(MediaLogicManager.DeviceCreateMedia, "/device/media/create")
        self.api.add_resource(MediaLogicManager.UploadMedia, '/media/upload/<media_id>')
        self.api.add_resource(MediaLogicManager.DeviceUploadMedia, '/device/media/upload/<media_id>')
        self.api.add_resource(MediaLogicManager.MediaRequest, '/media/retrieve')
        self.api.add_resource(MediaLogicManager.DeviceMediaRequest, '/device/media/retrieve')
        self.api.add_resource(MediaLogicManager.DeleteMedia, '/media/delete')
        self.api.add_resource(MediaLogicManager.DeviceDeleteMedia, '/device/media/delete')
        # BASIC MEDIA ROUTES
        self.api.add_resource(MediaManager.MediaDelete, '/admin/media/delete')
        self.api.add_resource(MediaManager.MediaInfo, '/media/info')
        self.api.add_resource(MediaManager.MediaInfoAdmin, '/admin/media/info')
        self.api.add_resource(MediaManager.MediaUpdate, '/admin/media/update')
        self.api.add_resource(MediaManager.MediaList, '/media/list')
        self.api.add_resource(MediaManager.DeviceMediaInfo, '/device/media/info')
        self.api.add_resource(MediaManager.DeviceMediaList, '/device/media/list')
        # DEVICE ROUTES
        self.api.add_resource(DeviceManager.DeviceAdd, '/admin/device/add')
        self.api.add_resource(DeviceManager.DeviceUpdate, '/device/update')
        self.api.add_resource(DeviceManager.DeviceInfo, '/user/device/info')
        self.api.add_resource(DeviceManager.DeviceDelete, '/admin/device/delete')
        self.api.add_resource(DeviceManager.DeviceActivate, '/admin/device/activate')
        self.api.add_resource(DeviceManager.DeviceLogin, '/device/authenticate')
        self.api.add_resource(DeviceManager.DeviceCredentials, '/admin/device/credentials')
        self.api.add_resource(DeviceManager.DeviceLogout, '/device/logout')
        self.api.add_resource(DeviceManager.UsernameAvailability, '/device/username/available')
        self.api.add_resource(DeviceManager.CheckDeviceToken, '/device/token/verify')
        self.api.add_resource(DeviceManager.ModifyDevicePassword, '/device/modify/password')
        self.api.add_resource(DeviceManager.InfoForDevice, '/device/info')
        # DEVICE MESSAGE ROUTES
        self.api.add_resource(DeviceMessageManager.DeviceMessageCreate, '/admin/device/message/create')
        self.api.add_resource(DeviceMessageManager.DeviceMessageDelete, '/device/message/delete')
        self.api.add_resource(DeviceMessageManager.DeviceMessageInfo, '/device/message/info')
        self.api.add_resource(DeviceMessageManager.DeviceMessageList, '/device/message/list')
        self.api.add_resource(DeviceMessageManager.DeviceMessageUpdate, '/device/message/update')
        # PAYMENT ROUTES
        self.api.add_resource(PaymentManager.FakePayment, '/device/buy')
        # API ROUTE
        self.api.add_resource(AccountManager.CreateApiToken, '/api/token')
        self.api.add_resource(Facebook.WebHookMessenger, '/api/messenger/webhook')
        self.api.add_resource(Hangout.WebHookHangout, '/api/hangout/webhook')

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
    with neo.app.app_context():
        User.CreateNeoAdmin(config.admin_password)
        init_default_content(config.beta_user1_password, config.beta_user2_password)
    return neo.app
