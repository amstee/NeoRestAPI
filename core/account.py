from config.database import db
from models.User import User as UserModel
from utils.apiUtils import *
from exceptions.account import *


def create(email, password, first_name, last_name, birthday):
    try:
        if db.session.query(UserModel).filter(UserModel.email == email).first() is not None:
            raise EmailAlreadyUsed
        UserModel(email=email, password=password, first_name=first_name, last_name=last_name, birthday=birthday)
        db.session.commit()
        response = jsonify({"success": True})
        response.status_code = 201
    except AccountException:
        response = jsonify({"success": False, "message": AccountException.message})
        response.status_code = AccountException.status_code
    return response


def login(email, password):
    try:
        user = db.session.query(UserModel).filter_by(email=email).first()
        if user is None:
            raise UserNotFound
        token = user.authenticate(password)
        resp = jsonify({"success": True, "token": token})
        resp.status_code = 200
        user.notify_circles({'event': 'connect', 'user': user.email})
    except AccountException:
        resp = jsonify({"success": False, "message": AccountException.message})
        resp.status_code = AccountException.status_code
    return resp


def modify_password(email, prev, new):
    try:
        user = db.session.query(UserModel).filter_by(email=email).first()
        if user is None:
            raise UserNotFound
        if not user.check_password(prev):
            raise MismatchingPassword
        user.update_password(new)
        response = jsonify({"success": True})
        response.status_code = 200
    except AccountException:
        resp = jsonify({"success": False, "message": AccountException.message})
        resp.status_code = AccountException.status_code
    return response


def check_token(json_token):
    try:
        UserModel.decode_auth_token(json_token)
        response = jsonify({"success": True, "message": "Le token json est valide"})
        response.status_code = 200
    except AccountException:
        response = jsonify({"success": False, "message": AccountException.message})
        response.status_code = AccountException.status_code
    return response


def logout(token):
    try:
        user = UserModel.decode_auth_token(token)
        if user is None:
            raise UserNotFound
        user.disconnect()
        user.notify_circles({'event': 'disconnect', 'user': user.email})
        response = jsonify({"success": True})
        response.status_code = 200
    except AccountException:
        response = jsonify({"success": False, "message": AccountException.message})
        response.status_code = AccountException.status_code
    return response


def get_info(user_id, client, is_device):
    try:
        user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            raise UserNotFound
        if is_device and not client.circle.has_member(user):
            raise NotAllowedToSeeUser
        response = jsonify({"success": True, "content": user.get_content()})
        response.status_code = 200
    except AccountException:
        response = jsonify({"success": False, "message": AccountException.message})
        response.status_code = AccountException.status_code
    return response


def update(content, user):
    try:
        email = None if 'email' not in content else content['email']
        first_name = None if 'first_name' not in content else content['first_name']
        last_name = None if 'last_name' not in content else content['last_name']
        birthday = None if 'birthday' not in content else content['birthday']
        user.update_content(email=email, first_name=first_name, last_name=last_name, birthday=birthday)
        resp = jsonify({"success": True})
        resp.status_code = 200
    except AccountException:
        response = jsonify({"success": False, "message": AccountException.message})
        response.status_code = AccountException.status_code
    return response


def is_email_available(email):
    try:
        user = db.session.query(UserModel).filter(UserModel.email == email).first()
        if user is not None:
            response = jsonify({"success": False})
        else:
            response = jsonify({"success": True})
        response.status_code = 200
    except AccountException:
        response = jsonify({"success": False, "message": AccountException.message})
        response.status_code = AccountException.status_code
    return response


def promote_admin(user_id):
    try:
        user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            raise UserNotFound
        user.promote_admin()
        response = jsonify({"success": True})
        response.status_code = 200
    except AccountException:
        response = jsonify({"success": False, "message": AccountException.message})
        response.status_code = AccountException.status_code
    return response


def create_api_token(user):
    try:
        token = user.encode_api_token()
        response = jsonify({"success": True, "api_token": token})
        response.status_code = 200
    except AccountException:
        response = jsonify({"success": False, "message": AccountException.message})
        response.status_code = AccountException.status_code
    return response
