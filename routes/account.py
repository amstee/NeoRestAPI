from flask import request
from flask_restful import Resource
from flask.ext.jsonpify import jsonify
from dateutil import parser as dateparser
from flask_httpauth import HTTPBasicAuth
from source.database import db_session
from models.User import User as UserModel
from utils.decorators import securedRoute, checkContent

auth = HTTPBasicAuth()

class AccountCreate(Resource):
    def get(sefl):
        content = request.args.get('email')
        user = db_session.query(UserModel).filter(UserModel.email == content)
        resp = jsonify(user.getNonSensitiveContent())
        return resp

    @checkContent
    def post(self, content):
        try:
            new_user = UserModel(email=content['email'], password=content['password'], first_name=content['first_name'],
                    last_name=content['last_name'], birthday=content["birthday"])
            db_session.add(new_user)
            db_session.commit()
            resp = jsonify({"success": True})
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
        return resp

class AccountLogin(Resource):
    @checkContent
    def post(self, content):
        user = db_session.query(UserModel).filter_by(email=content["email"]).first()
        if user != None:
            res, data = user.Authenticate(content["password"])
            if res is True:
                resp = jsonify({"success": True, "token": data})
            else:
                resp = jsonify({"success": False, "message": data})
        else:
            resp = jsonify({"succes": False, "message": "User not found"})
        return resp

class AccountLogout(Resource):
    @checkContent
    def post(self):
        content = request.get_json()
        res, data = UserModel.decodeAuthToken(content["token"])
        if (res is True):
            disco_res, message = data.disconnect()
            if disco_res is True:
                resp = jsonify({"success": True})
            else:
                resp = jsonify({"success": False, "message": message})
        else:
            resp = jsonify({"success": False, "message": data})
        return resp

class AccountInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        resp = jsonify(user.getNonSensitiveContent())
        return resp

class AccountModify(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        user.updateContent(email=content["email"], password=content["password"],
                           first_name=content["first_name"], last_name=content["last_name"],
                        birthday=content["birthday"], searchText=content["searchText"],
                           created=content["created"], updated=content["updated"])
        resp = jsonify({"success" : True})
        return resp