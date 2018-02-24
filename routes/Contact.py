from flask_restful import Resource
from source.database import db_session
from utils.decorators import checkContent
from utils.decorators import securedRoute
from models.Contact import Contact
from models.User import User
from utils.apiUtils import *

class ContactAdd(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            newContact = User.query.filter(User.email == content["email"]).first()
            if newContact is not None:
                #temporary
                contact = Contact(user=user, platform="NEO", first_name=str(newContact.first_name), last_name=str(newContact.last_name))
                db_session.commit()
                resp = SUCCESS()
            else:
                resp = FAILED("User with email '%s' not found" % content["email"])
        except Exception as e:
            resp = FAILED(e)
            resp.status_code = 409
        return resp

class ContactUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contact = Contact.query.filter(Contact.id == content["contact_id"] and Contact.user == user).first()
            if contact is not None:
                content['first_name'] = None if 'first_name' not in content else content['first_name']
                content['last_name'] = None if 'last_name' not in content else content['last_name']
                contact.updateContent(first_name=content["first_name"], last_name=content["last_name"], user=user)
                resp = SUCCESS()
            else:
                resp = FAILED("Contact with id '%d' not found" % content["contact_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp

class ContactList(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        arr = []
        try:
            for contact in user.contact:
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
            contact = db_session.query(Contact).filter(Contact.id == content["contact_id"] and Contact.user == user).first()
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
            for contacts in user.contact:
                if contacts.id == content["contact_id"]:
                    Contact.query.filter(Contact.id == content['contact_id']).delete()
                    db_session.commit()
                    resp = SUCCESS()
                else:
                    resp = FAILED("Contact with id %d not found" % content["contact_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp