from flask import request
from flask_restful import Resource
from flask.ext.jsonpify import jsonify
from source.database import db_session
from models.User import User as UserModel
from utils.decorators import securedRoute, checkContent

class AccountCreate(Resource):
    def get(sefl):
        content = request.args.get('email')
        user = db_session.query(UserModel).filter(UserModel.email == content)
        resp = jsonify(user.getNonSensitiveContent())
        resp.status_code = 200
        return resp

    @checkContent
    def post(self, content):
        try:
            new_user = UserModel(email=content['email'], password=content['password'], first_name=content['first_name'],
                    last_name=content['last_name'], birthday=content["birthday"])
            db_session.add(new_user)
            db_session.commit()
            resp = jsonify({"success": True})
            resp.status_code = 201
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 409
        return resp

class AccountLogin(Resource):
    @checkContent
    def post(self, content):
        user = db_session.query(UserModel).filter_by(email=content["email"]).first()
        if user != None:
            res, data = user.Authenticate(content["password"])
            if res is True:
                resp = jsonify({"success": True, "token": data})
                resp.status_code = 200
            else:
                resp = jsonify({"success": False, "message": data})
                resp.status_code = 401
        else:
            resp = jsonify({"succes": False, "message": "User not found"})
            resp.status_code = 401
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
                resp.status_code =  403
        else:
            resp = jsonify({"success": False, "message": data})
            resp.status_code = 403
        return resp

class AccountInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        resp = jsonify(user.getNonSensitiveContent())
        resp.status_code = 200
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
        resp.status_code = 200
        return resp