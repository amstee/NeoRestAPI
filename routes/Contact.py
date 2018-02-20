from flask_restful import Resource
from utils.decorators import checkContent
from utils.decorators import securedRoute
from models.Contact import Contact
from models.Device import Device
from source.database import db_session
from utils.apiUtils import *

class ContactAdd(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                contact = Contact(platform=content["platform"], first_name=content["first_name"], last_name=content["last_name"], device=device)
                db_session.commit()
                resp = SUCCESS()
            else:
                resp = FAILED("Device with id '%d' not found" % content["device_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp

class ContactUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contact = db_session.query(Contact).filter(Contact.id == content["contact_id"]).first()
            device = None
            if content["device_id"] is not None and type(content["device_id"]) is int:
                device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
                if device is not None:
                    contact.updateContent(content["platform"], content["first_name"], content["last_name"],
                                          content["created"], content["updated"], device)
                    resp = SUCCESS()
                else:
                    resp = FAILED("Device with id '%d' not found" % content["device_id"])
            else:
                contact.updateContent(content["platform"], content["first_name"], content["last_name"],
                                      content["created"], content["updated"], device)
                resp = SUCCESS()
        except Exception as e:
            resp = FAILED(e)
        return resp

class ContactsInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        arr = []
        try:
            for contact in user.contacts:
                arr.append(contact.getNonSensitiveContent())
                resp = jsonify({"success": True, "content": arr})
        except Exception as e:
            resp = FAILED(e)
        return resp

class ContactInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contact = db_session.query(Contact).filter(Contact.id == content["contact_id"]).first()
            if contact is not None:
                resp = jsonify({"success": True, "content": contact.getNonSensitiveContent()})
            else:
                resp = FAILED("Contact with id %d could not be found" % content["contact_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp

class ContactDelete(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contact = db_session.query(Contact).filter(Contact.id == content["contact_id"]).first()
            if contact is not None:
                contact.delete()
                resp = SUCCESS()
            else:
                resp = FAILED("Contact with id %d nto found" % content["contact_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp