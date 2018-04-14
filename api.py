from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import routes.Account as AccountManager
import routes.Device as DeviceManager
import routes.Circle as CircleManager
import routes.CircleLogic as CircleLogicManager
import routes.Payment as PaymentManager
import routes.Message as BasicMessageManager
import routes.Media as MediaManager
import config.database as db

app = Flask(__name__)
api = Api(app)
CORS(app)

# ACCOUNT ROUTES
api.add_resource(AccountManager.AccountCreate, '/account/create')
api.add_resource(AccountManager.AccountLogin, '/account/login')
api.add_resource(AccountManager.AccountLogout, '/account/logout')
api.add_resource(AccountManager.AccountInfo, '/account/info')
api.add_resource(AccountManager.AccountModify, '/account/modify')
api.add_resource(AccountManager.MailAvailability, '/account/create/available')
api.add_resource(AccountManager.ModifyPassword, '/account/modify/password')
api.add_resource(AccountManager.ForgotPassword, '/account/forgot')
api.add_resource(AccountManager.CheckToken, '/token/verify')
api.add_resource(AccountManager.PromoteAdmin, '/admin/account/promote')

# CIRCLE LOGIC ROUTES
api.add_resource(CircleLogicManager.CircleInvite, '/circle/invite')
api.add_resource(CircleLogicManager.CircleJoin, '/circle/join')
api.add_resource(CircleLogicManager.CircleReject, '/circle/reject')
api.add_resource(CircleLogicManager.CircleQuit, '/circle/quit')
api.add_resource(CircleLogicManager.CircleKick, '/circle/kick')

# CIRCLE BASIC ROUTES
api.add_resource(CircleManager.CircleCreate, '/circle/create')
api.add_resource(CircleManager.CircleUpdate, '/circle/update')
api.add_resource(CircleManager.CircleDelete, '/admin/circle/delete')
api.add_resource(CircleManager.CircleInfo, '/circle/info')
api.add_resource(CircleManager.CircleList, '/circle/list')

# BASIC MESSAGE ROUTES
api.add_resource(BasicMessageManager.MessageCreate, '/admin/message/create')
api.add_resource(BasicMessageManager.MessageDelete, '/message/delete')
api.add_resource(BasicMessageManager.MessageInfo, '/message/info')
api.add_resource(BasicMessageManager.MessageUpdate, '/message/update')
api.add_resource(BasicMessageManager.MessageList, '/conversation/message/list')

# BASIC MEDIA ROUTES
api.add_resource(MediaManager.MediaCreate, '/admin/media/create')
api.add_resource(MediaManager.MediaDelete, '/admin/media/delete')
api.add_resource(MediaManager.MediaInfo, '/media/info')
api.add_resource(MediaManager.MediaInfoAdmin, '/admin/media/info')
api.add_resource(MediaManager.MediaUpdate, '/admin/media/update')
api.add_resource(MediaManager.MediaList, '/media/list')

# DEVICE ROUTES
api.add_resource(DeviceManager.DeviceAdd, '/admin/device/add')
api.add_resource(DeviceManager.DeviceUpdate, '/device/update')
api.add_resource(DeviceManager.DeviceInfo, '/device/info')
api.add_resource(DeviceManager.DeviceDelete, '/admin/device/delete')

# PAYMENT ROUTES
api.add_resource(PaymentManager.FakePayment, '/device/buy')

db.init_db()

if __name__ == '__main__':
     app.run(port=5000, host='0.0.0.0')