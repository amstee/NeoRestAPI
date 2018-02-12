from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify
from datetime import datetime
from dateutil import parser as dateparser

from routes.account import *
from routes.accountDevice import *

import binascii
import os

app = Flask(__name__)
api = Api(app)


api.add_resource(AccountCreate, '/account/create')
api.add_resource(AccountLogin, '/account/login')
api.add_resource(AccountLogout, '/account/logout')
api.add_resource(AccountInfo, '/account/info')
api.add_resource(AccountModify, '/account/modify')

api.add_resource(AccountDeviceAdd, '/account/device/add')
api.add_resource(AccountDeviceList, '/account/device/list')


if __name__ == '__main__':
     app.run(port=5002, host='0.0.0.0')