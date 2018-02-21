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

# CONTACT ROUTES
api.add_resource(ContactManager.ContactAdd, '/account/contact/create')
api.add_resource(ContactManager.ContactUpdate, '/account/contact/update')
api.add_resource(ContactManager.ContactInfo, '/account/contact/info')
api.add_resource(ContactManager.ContactsInfo, '/account/contact/contactsInfo')
api.add_resource(ContactManager.ContactDelete, '/account/contact/delete')

# DEVICE ROUTES
api.add_resource(DeviceManager.DeviceAdd, '/device/create')
api.add_resource(DeviceManager.DeviceUpdate, '/device/update')
api.add_resource(DeviceManager.DeviceInfo, '/device/info')
api.add_resource(DeviceManager.AccountDevices, '/device/accountDevices')
api.add_resource(DeviceManager.DeviceDelete, '/device/delete')

# DEVICE USER ROUTES
api.add_resource(DeviceUserManager.DeviceUserCreate, '/device/user/create')
api.add_resource(DeviceUserManager.DeviceUserUpdate, '/device/user/update')
api.add_resource(DeviceUserManager.DeviceUserInfo, '/device/user/info')
api.add_resource(DeviceUserManager.DeviceUserDelete, '/device/user/delete')


db.init_db()


if __name__ == '__main__':
     app.run(port=5000, host='0.0.0.0')