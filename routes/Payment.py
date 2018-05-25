from flask import request
from flask_restful import Resource
from config.database import db_session
from models.Device import Device
from models.Circle import Circle
from models.User import User as UserModel
from utils.contentChecker import contentChecker
from utils.decorators import securedRoute, checkContent
from models.UserToCircle import UserToCircle
from utils.apiUtils import *
from config.paypal import *


class PaypalCreatePayment(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "https://server.neo.ovh/payement/execute",
                "cancel_url": "https://server.neo.ovh/",
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Device NEO",
                        "sku": "NEO",
                        "price": "39.99",
                        "currency": "EUR",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": "39.99",
                    "currency": "EUR"
                },
                "description": "The user ['%s' '%s'] bought the program NEO for 39.99Euros"%(user.first_name, user.last_name)
            }]
        })
        if (payment.create()):
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    return jsonify({"success": True, "content": {"approval_url": approval_url}})
            return FAILED("Url de validation introuvable")
        else:
            return FAILED(str(payment.error))


class FakePayment(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("circle_id")
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            if circle is not None:
                if not circle.hasMember(user):
                    return FAILED("Cet utilisateur ne fait pas parti du cercle spécifié")
                link = db_session.query(UserToCircle).filter(UserToCircle.circle_id == circle.id,
                                                            UserToCircle.user_id == user.id).first();
                if link is None:
                    return FAILED("Cet utilisateur ne fait pas parti du cercle spécifié")
                link.privilege = "ADMIN"
                device = Device(name=content["device_name"] if "device_name" in content else "Papi/Mamie")
                circle.device = device
                device.circle = circle
                db_session.commit()
                return jsonify({"success": True, "content": device.getContent()})
            return FAILED("Cercle spécifié introuvable")
        except Exception as e:
            return FAILED(e)
