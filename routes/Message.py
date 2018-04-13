from flask import request
from flask_restful import Resource
from config.database import db_session
from models.User import User as UserModel
from utils.decorators import securedRoute, checkContent, securedAdminRoute
from utils.apiUtils import *

def MessageCreate(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            pass
        except Exception as e:
            return FAILED(e)

def MessageDelete(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            pass
        except Exception as e:
            return FAILED(e)

def MessageInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            pass
        except Exception as e:
            return FAILED(e)

def MessageList(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            pass
        except Exception as e:
            return FAILED(e)

def MessageUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            pass
        except Exception as e:
            return FAILED(e)