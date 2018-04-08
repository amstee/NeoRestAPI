from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import routes.Account as AccountManager
import routes.Device as DeviceManager
import routes.Circle as CircleManager
import routes.CircleLogic as CircleLogicManager
import source.database as db

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
api.add_resource(AccountManager.modifyPassword, '/account/modify/password')
api.add_resource(AccountManager.forgotPassword, '/account/forgot')
api.add_resource(AccountManager.checkToken, '/token/verify')

# CIRCLE LOGIC ROUTES
api.add_resource(CircleLogicManager.CircleInvite, '/circle/invite')
api.add_resource(CircleLogicManager.CircleJoin, '/circle/join')
api.add_resource(CircleLogicManager.CircleReject, '/circle/reject')
api.add_resource(CircleLogicManager.CircleQuit, '/circle/quit')
api.add_resource(CircleLogicManager.CircleKick, '/circle/kick')

# CIRCLE BASIC ROUTES
api.add_resource(CircleManager.CircleCreate, '/circle/create')
api.add_resource(CircleManager.CircleUpdate, '/circle/update')
api.add_resource(CircleManager.CircleDelete, '/circle/delete')
api.add_resource(CircleManager.CircleInfo, '/circle/info')
api.add_resource(CircleManager.CircleList, '/circle/list')

# DEVICE ROUTES
api.add_resource(DeviceManager.DeviceAdd, '/account/device/add')
api.add_resource(DeviceManager.DeviceUpdate, '/account/device/update')
api.add_resource(DeviceManager.DeviceInfo, '/account/device/info')
api.add_resource(DeviceManager.DeviceDelete, '/account/device/delete')

db.init_db()

if __name__ == '__main__':
     app.run(port=5000, host='0.0.0.0')