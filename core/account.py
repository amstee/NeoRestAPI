from config.database import db
from models.User import User as UserModel
from exceptions import account as e_account


def create(email, password, first_name, last_name, birthday):
    try:
        if db.session.query(UserModel).filter(UserModel.email == email).first() is not None:
            raise e_account.EmailAlreadyUsed
        UserModel(email=email, password=password, first_name=first_name, last_name=last_name, birthday=birthday)
        db.session.commit()
        response = {
            "data": {"success": True},
            "status_code": 201
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def login(email, password):
    try:
        user = db.session.query(UserModel).filter_by(email=email).first()
        if user is None:
            raise e_account.UserNotFound
        token = user.authenticate(password)
        user.notify_circles({'event': 'connect', 'user': user.email})
        response = {
            "data": {"success": True, "token": token},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def modify_password(email, prev, new):
    try:
        user = db.session.query(UserModel).filter_by(email=email).first()
        if user is None:
            raise e_account.UserNotFound
        if not user.check_password(prev):
            raise e_account.MismatchingPassword
        user.update_password(new)
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def check_token(json_token):
    try:
        UserModel.decode_auth_token(json_token)
        response = {
            "data": {"success": True, "message": "Le token json est valide"},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def logout(token):
    try:
        user = UserModel.decode_auth_token(token)
        if user is None:
            raise e_account.UserNotFound
        user.disconnect()
        user.notify_circles({'event': 'disconnect', 'user': user.email})
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def get_info(user_id, client, is_device):
    try:
        user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            raise e_account.UserNotFound
        if is_device and not client.circle.has_member(user):
            raise e_account.NotAllowedToSeeUser
        response = {
            "data": {"success": True, "content": user.get_content()},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def update(content, user):
    try:
        email = None if 'email' not in content else content['email']
        first_name = None if 'first_name' not in content else content['first_name']
        last_name = None if 'last_name' not in content else content['last_name']
        birthday = None if 'birthday' not in content else content['birthday']
        user.update_content(email=email, first_name=first_name, last_name=last_name, birthday=birthday)
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def is_email_available(email):
    try:
        user = db.session.query(UserModel).filter(UserModel.email == email).first()
        if user is not None:
            data = {"success": False}
        else:
            data = {"success": True}
        response = {
            "data": data,
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def promote_admin(user_id):
    try:
        user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            raise e_account.UserNotFound
        user.promote_admin()
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def create_api_token(user):
    try:
        token = user.encode_api_token()
        response = {
            "data": {"success": True, "api_token": token},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def add_ios_token(ios_token, user):
    try:
        user.ios_token = ios_token
        db.session.commit()
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def add_android_token(android_token, user):
    try:
        old_user = db.session.query(UserModel).filter(UserModel.android_token == android_token).first()
        if old_user is not None:
            old_user.android_token = None
        user.android_token = android_token
        db.session.commit()
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_account.AccountException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response
