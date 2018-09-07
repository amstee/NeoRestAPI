from flask import request
from config.database import db
from models.Device import Device
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from utils.apiUtils import *
from utils.log import logger_set

logger = logger_set(__name__)


def fake_pay(content, circle_id, user):
    logger.info("[%s] [%s] [%s] [%s] [%s]",
                request.method, request.host, request.path, request.content_type, request.data)
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is not None:
            if not circle.has_member(user):
                return FAILED("Cet utilisateur ne fait pas parti du cercle spécifié")
            link = db.session.query(UserToCircle).filter(UserToCircle.circle_id == circle.id,
                                                         UserToCircle.user_id == user.id).first()
            if link is None:
                return FAILED("Cet utilisateur ne fait pas parti du cercle spécifié")
            link.privilege = "ADMIN"
            device = Device(name=content["device_name"] if "device_name" in content else "Papi/Mamie")
            circle.device = device
            device.circle = circle
            db.session.commit()
            return jsonify({"success": True, "content": device.get_content()})
        return FAILED("Cercle spécifié introuvable")
    except Exception as e:
        return FAILED(e)
