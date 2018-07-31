from config.database import db_session
from models.User import User
from models.Device import Device


def get_dest(json):
    if "email" in json:
        return False, db_session.query(User).filter(User.email == json["email"]).first()
    if "user_id" in json:
        return False, db_session.query(User).filter(User.id == json["user_id"]).first()
    if "device_id" in json:
        return True, db_session.query(Device).filter(Device.id == json["device_id"]).first()
    return False, None