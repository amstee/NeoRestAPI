from flask import request
from flask_restful import Resource
from config.database import db_session
from models.Media import Media
from models.Device import Device
from models.Message import Message
from utils.decorators import checkContent, securedAdminRoute, securedDeviceRoute
from models.Conversation import Conversation
from utils.contentChecker import contentChecker
from utils.apiUtils import *

class FirstDeviceMessageSend(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        pass

class DeviceMessageSend(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        pass