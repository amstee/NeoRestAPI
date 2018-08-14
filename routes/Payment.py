from flask_restful import Resource
from config.database import db_session
from models.Device import Device
from models.Circle import Circle
from utils.contentChecker import content_checker
from utils.decorators import secured_route, check_content
from models.UserToCircle import UserToCircle
from utils.apiUtils import *


class FakePayment(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            circle = db_session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is not None:
                if not circle.has_member(user):
                    return FAILED("Cet utilisateur ne fait pas parti du cercle spécifié")
                link = db_session.query(UserToCircle).filter(UserToCircle.circle_id == circle.id,
                                                             UserToCircle.user_id == user.id).first()
                if link is None:
                    return FAILED("Cet utilisateur ne fait pas parti du cercle spécifié")
                link.privilege = "ADMIN"
                device = Device(name=content["device_name"] if "device_name" in content else "Papi/Mamie")
                circle.device = device
                device.circle = circle
                db_session.commit()
                return jsonify({"success": True, "content": device.get_content()})
            return FAILED("Cercle spécifié introuvable")
        except Exception as e:
            return FAILED(e)
