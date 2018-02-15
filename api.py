from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import routes.Account as AccountManager
import routes.Device as DeviceManager
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

# DEVICE ROUTES
api.add_resource(DeviceManager.DeviceAdd, '/device/create')
api.add_resource(DeviceManager.DeviceUpdate, '/device/Update')
api.add_resource(DeviceManager.DeviceInfo, '/device/Info')
api.add_resource(DeviceManager.AccountDevices, '/device/AccountDevices')
api.add_resource(DeviceManager.DeviceDelete, '/device/delete')

# DEVICE USER ROUTES

# CONTACT ROUTES



db.init_db()

# api.add_resource(AccountDeviceAdd, '/account/device/add')
# api.add_resource(AccountDeviceList, '/account/device/list')

if __name__ == '__main__':
     app.run(port=5000, host='0.0.0.0')