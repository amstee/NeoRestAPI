from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from routes.account import *
import source.database as db

app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(AccountCreate, '/account/create')
api.add_resource(AccountLogin, '/account/login')
api.add_resource(AccountLogout, '/account/logout')
api.add_resource(AccountInfo, '/account/info')
api.add_resource(AccountModify, '/account/modify')

db.init_db()

# api.add_resource(AccountDeviceAdd, '/account/device/add')
# api.add_resource(AccountDeviceList, '/account/device/list')

if __name__ == '__main__':
     app.run(port=5000, host='0.0.0.0')