from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from models.User import User
import routes.Account as AccountManager
import routes.Device as DeviceManager
import routes.Circle as CircleManager
import routes.CircleLogic as CircleLogicManager
import routes.Payment as PaymentManager
import routes.Message as BasicMessageManager
import routes.MessageLogic as MessageLogicManager
import routes.Media as MediaManager
import routes.MediaLogic as MediaLogicManager
import routes.DeviceMessage as DeviceMessageManager
import routes.ConversationLogic as ConversationLogicManager
import routes.Conversation as ConversationManager
import routes.DeviceMessageLogic as DeviceMessageLogicManager
import routes.Facebook as Facebook
import config.database as db

class neoapi(object):
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)

        # ACCOUNT ROUTES
        self.api.add_resource(AccountManager.AccountCreate, '/account/create')
        self.api.add_resource(AccountManager.AccountLogin, '/account/login')
        self.api.add_resource(AccountManager.AccountLogout, '/account/logout')
        self.api.add_resource(AccountManager.AccountInfo, '/account/info')
        self.api.add_resource(AccountManager.AccountModify, '/account/modify')
        self.api.add_resource(AccountManager.MailAvailability, '/account/create/available')
        self.api.add_resource(AccountManager.ModifyPassword, '/account/modify/password')
        self.api.add_resource(AccountManager.ForgotPassword, '/account/forgot')
        self.api.add_resource(AccountManager.CheckToken, '/token/verify')
        self.api.add_resource(AccountManager.PromoteAdmin, '/admin/account/promote')
        # CIRCLE LOGIC ROUTES
        self.api.add_resource(CircleLogicManager.CircleInvite, '/circle/invite')
        self.api.add_resource(CircleLogicManager.CircleJoin, '/circle/join')
        self.api.add_resource(CircleLogicManager.CircleReject, '/circle/reject')
        self.api.add_resource(CircleLogicManager.CircleQuit, '/circle/quit')
        self.api.add_resource(CircleLogicManager.CircleKick, '/circle/kick')
        # CIRCLE BASIC ROUTES
        self.api.add_resource(CircleManager.CircleCreate, '/circle/create')
        self.api.add_resource(CircleManager.CircleUpdate, '/circle/update')
        self.api.add_resource(CircleManager.CircleDelete, '/admin/circle/delete')
        self.api.add_resource(CircleManager.CircleInfo, '/circle/info')
        self.api.add_resource(CircleManager.CircleList, '/circle/list')
        #self.api.add_resource(CircleManager.CircleDeviceInfo, '/device/circle/info')
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
        self.api.add_resource(MediaLogicManager.MediaRequest, '/media/get-media')
        # BASIC MEDIA ROUTES
        self.api.add_resource(MediaManager.MediaCreate, '/admin/media/create')
        self.api.add_resource(MediaManager.MediaDelete, '/admin/media/delete')
        self.api.add_resource(MediaManager.MediaInfo, '/media/info')
        self.api.add_resource(MediaManager.MediaInfoAdmin, '/admin/media/info')
        self.api.add_resource(MediaManager.MediaUpdate, '/admin/media/update')
        self.api.add_resource(MediaManager.MediaList, '/media/list')
        # DEVICE ROUTES
        self.api.add_resource(DeviceManager.DeviceAdd, '/admin/device/add')
        self.api.add_resource(DeviceManager.DeviceUpdate, '/device/update')
        self.api.add_resource(DeviceManager.DeviceInfo, '/device/info')
        self.api.add_resource(DeviceManager.DeviceDelete, '/admin/device/delete')
        self.api.add_resource(DeviceManager.DeviceActivate, '/device/activate')
        self.api.add_resource(DeviceManager.DeviceLogin, '/device/authenticate')
        self.api.add_resource(DeviceManager.DeviceCredentials, '/admin/device/credentials')
        self.api.add_resource(DeviceManager.DeviceLogout, '/device/logout')
        self.api.add_resource(DeviceManager.UsernameAvailability, '/device/username/available')
        self.api.add_resource(DeviceManager.CheckDeviceToken, '/device/token/verify')
        self.api.add_resource(DeviceManager.ModifyDevicePassword, '/device/modify/password')
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
        self.api.add_resource(Facebook.Webhook, '/api/messenger/webhook')

        db.init_db()
        User.CreateNeoAdmin()

    def activate_testing(self):
        self.app.config['TESTING'] = True
        return self.app.test_client()

if __name__ == '__main__':
    neo = neoapi()
    neo.app.run(port=5000, host='0.0.0.0')