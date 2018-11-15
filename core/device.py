from models.Device import Device
from models.Circle import Circle
from models.User import User
from config.database import db
from exceptions import device as e_device
from exceptions import account as e_account
from exceptions import circle as e_circle


def is_username_available(username):
    try:
        device = db.session.query(Device).filter(Device.username == username).first()
        if device is not None:
            raise e_device.DeviceNameAlreadyExist
        response = {
                "data": {"success": True},
                "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def logout(device_token):
    try:
        device = Device.decode_auth_token(device_token)
        device.circle.notify_users(p2={'event': 'device', 'type': 'disconnect', 'device_id': device.id})
        response = {
                "data": {"success": True},
                "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def check_token(_, __):
    try:
        response = {
                "data": {"success": True},
                "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def modify_password(username, prev, new):
    try:
        device = db.session.query(Device).filter(Device.username == username).first()
        if device is None:
            raise e_device.DeviceNotFound
        if device.check_password(prev) is False:
            raise e_device.MismatchOldPassword
        device.update_password(new)
        response = {
                "data": {"success": True},
                "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def login(username, password):
    try:
        device = db.session.query(Device).filter(Device.username == username).first()
        if device is None:
            raise e_device.DeviceNotFound
        token = device.authenticate(password)
        device.circle.notify_users(p2={'event': 'device', 'type': 'connect', 'device_id': device.id})
        response = {
            "data": {"success": True, "device_token": token},
            "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def info(device_id, client, is_device):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is None:
            raise e_device.DeviceNotFound
        if (not is_device and not device.circle.has_member(client)) and (is_device and device.id != client.id):
            raise e_device.NotPartOfDeviceCircle
        response = {
            "data": {"success": True, "content": device.get_content()},
            "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def update(content, device_id, client, is_device):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is None:
            raise e_device.DeviceNotFound
        if not is_device and not device.circle.has_admin(client):
            raise e_account.InsufficientAccountRight
        if is_device and device_id != client.id:
            raise e_device.DeviceForbiddenAccess
        device.update_content(name=content['name'] if "name" in content else None)
        device.circle.notify_users(p2={'event': 'device', 'type': 'update', 'device_id': device.id})
        response = {
                "data": {"success": True},
                "status_code": 200
        }
    except (e_device.DeviceException, e_account.AccountException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def admin_credentials(device_id):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is None:
            raise e_device.DeviceNotFound
        response = {
                "data": {
                    "success": True,
                    "content": {
                        "key": device.key,
                        "username": device.username,
                        "password": device.get_pre_activation_password()
                    }
                },
                "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def admin_activate(device_id, activation_key):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is None:
            raise e_device.DeviceNotFound
        activated = device.activate(activation_key)
        if activated is False:
            raise e_device.InvalidActivationKey
        response = {
                "data": {"success": True},
                "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def admin_add(content, circle_id, name):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            raise e_circle.CircleNotFound
        new_device = Device(name=name, username=content["username"] if "username" in content else None)
        new_device.circle = circle
        db.session.commit()
        circle.notify_users('device created')
        response = {
                "data": {"success": True},
                "status_code": 200
        }
    except e_circle.CircleException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def admin_delete(device_id):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is None:
            raise e_device.DeviceNotFound
        db.session.delete(device)
        db.session.commit()
        response = {
                "data": {"success": True},
                "status_code": 200
        }
    except e_device.DeviceException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def admin_list(email):
    try:
        user = db.session.query(User).filter(User.email == email).first()
        not_found = True
        if user is None:
            raise e_account.UserNotFound
        if len(user.circle_link) == 0:
            raise e_device.NoDeviceForUser
        for link in user.circle_link:
            if link.privilege == "ADMIN":
                devices = db.session.query(Device).filter(Device.circle_id == link.circle_id)
                response = {
                    "data": {"success": True, "devices": [device.get_simple_content() for device in devices]},
                    "status_code": 200
                }
                not_found = False
        if not_found:
            raise e_device.NoDeviceForUser
    except (e_device.DeviceException, e_account.AccountException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response
