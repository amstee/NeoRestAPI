from flask import request
from flask_restful import Resource
from source.database import db_session
from models.User import User as UserModel
from utils.decorators import securedRoute, checkContent
from utils.apiUtils import *

class AccountCreate(Resource):
    def get(sefl):
        content = request.args.get('email')
        user = db_session.query(UserModel).filter(UserModel.email == content)
        resp = jsonify({"success":True, "content": user.getSimpleContent()})
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
            resp = jsonify({"succes": False, "message": "Utilisateur introuvable"})
            resp.status_code = 401
        return resp

class forgotPassword(Resource):
    @checkContent
    def post(self, content):
        return SUCCESS()

class modifyPassword(Resource):
    @checkContent
    def post(self, content):
        email = content["email"]
        prev = content["previous_password"]
        new = content["new_password"]
        user = db_session.query(UserModel).filter_by(email=email).first()
        if user != None:
            if user.checkPassword(prev):
                user.updatePassword(new)
                return SUCCESS()
            return FAILED("Le mot de passe de correspond pas")
        return FAILED("Utilisateur introuvable")


class checkToken(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        return jsonify({"success": True, "message": "Le token json est valide"})

class AccountLogout(Resource):
    @checkContent
    def post(self, content):
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
        resp = jsonify(user.getContent())
        resp.status_code = 200
        return resp

class AccountModify(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        content["email"] = None if 'email' not in content else content['email']
        content["first_name"] = None if 'first_name' not in content else content['first_name']
        content["last_name"] = None if 'last_name' not in content else content['last_name']
        content['birthday'] = None if 'birthday' not in content else content['birthday']
        content["searchText"] = None if 'searchText' not in content else content['searchText']
        user.updateContent(email=content["email"],
                           first_name=content["first_name"], last_name=content["last_name"],
                        birthday=content["birthday"], searchText=content["searchText"])
        resp = jsonify({"success" : True})
        resp.status_code = 200
        return resp

class MailAvailability(Resource):
    @checkContent
    def post(self, content):
        user = UserModel.query.filter(UserModel.email == content['email']).first()
        if user != None:
            resp = jsonify({"success" : False})
        else:
            resp = jsonify({"success" : True})
        resp.status_code = 200
        return resp