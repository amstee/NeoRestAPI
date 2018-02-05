from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify
from datetime import datetime
from dateutil import parser as dateparser

from routes.account import *

import binascii
import os

app = Flask(__name__)
api = Api(app)


api.add_resource(Account, '/account')
api.add_resource(User, '/account/<string:user>')

if __name__ == '__main__':
     app.run(port=5002, host='0.0.0.0')