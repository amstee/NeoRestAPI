from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import routes.Account as AccountManager
import routes.Device as DeviceManager
import routes.Contact as ContactManager
import routes.DeviceUser as DeviceUserManager
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
api.add_resource(DeviceManager.DeviceUpdate, '/device/update')
api.add_resource(DeviceManager.DeviceInfo, '/device/info')
api.add_resource(DeviceManager.AccountDevices, '/device/accountDevices')
api.add_resource(DeviceManager.DeviceDelete, '/device/delete')

# DEVICE USER ROUTES
api.add_resource(DeviceUserManager.DeviceUserCreate, '/deviceUser/create')
api.add_resource(DeviceUserManager.DeviceUserUpdate, '/deviceUser/update')
api.add_resource(DeviceUserManager.DeviceUserInfo, '/deviceUser/info')
api.add_resource(DeviceUserManager.DeviceUserDelete, '/deviceUser/delete')

# CONTACT ROUTES
api.add_resource(ContactManager.ContactAdd, '/contact/create')
api.add_resource(ContactManager.ContactUpdate, '/contact/update')
api.add_resource(ContactManager.ContactInfo, '/contact/info')
api.add_resource(ContactManager.ContactsInfo, '/contact/contactsInfo')
api.add_resource(ContactManager.ContactDelete, '/contact/delete')



db.init_db()

# api.add_resource(AccountDeviceAdd, '/account/device/add')
# api.add_resource(AccountDeviceList, '/account/device/list')

if __name__ == '__main__':
     app.run(port=5000, host='0.0.0.0')