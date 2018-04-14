from flask_restful import Resource
from config.database import db_session
from models.User import User as UserModel
from models.Circle import Circle
from models.CircleInvite import CircleInvite as CircleInviteModel
from utils.decorators import securedRoute, checkContent
from models.UserToCircle import UserToCircle
from utils.contentChecker import contentChecker
from utils.apiUtils import *


class CircleInvite(Resource):
    @checkContent
    @securedRoute
    def post(self, content):
        try:
            contentChecker("circle_id", "email")
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            if circle is not None:
                dest = db_session.query(UserModel).filter(UserModel.email==content["email"]).first()
                if dest is not None:
                    circle_invite = CircleInviteModel()
                    circle_invite.user = dest
                    circle_invite.circle = circle
                    db_session.commit()
                    return SUCCESS()
                return FAILED("Utilisateur spécifié introuvable")
            return FAILED("Cercle spécifié introuvable")
        except Exception as e:
            return FAILED(e)


class CircleJoin(Resource):
    @checkContent
    @securedRoute
    def post(self, content):
        try:
            contentChecker("invite_id")
            invite = db_session.query(CircleInvite).filter_by(CircleInviteModel.id == content["invite_id"]).first()
            if invite is not None:
                link = UserToCircle(privilege="MEMBRE")
                link.user = invite.user
                link.circle = invite.circle
                db_session.commit()
                return SUCCESS()
            return FAILED("Invitation introuvable")
        except Exception as e:
            return FAILED(e)


class CircleReject(Resource):
    @checkContent
    @securedRoute
    def post(self, content):
        try:
            contentChecker("invite_id")
            invite = db_session.query(CircleInvite).filter_by(CircleInviteModel.id == content["invite_id"]).first()
            if invite is not None:
                db_session.delete(invite)
                return SUCCESS()
            return FAILED("Invitation introuvable")
        except Exception as e:
            return FAILED(e)


class CircleQuit(Resource):
    @checkContent
    @securedRoute
    def post(self, content):
        try:
            contentChecker("link_id")
            link = db_session.query(UserToCircle).filter_by(UserToCircle.id == content["link_id"]).first()
            if link is not None:
                db_session.delete(link)
                return SUCCESS()
            return FAILED("Cercle introuvable")
        except Exception as e:
            return FAILED(e)


class CircleKick(Resource):
    @checkContent
    @securedRoute
    def post(self, content):
        try:
            contentChecker("email", "circle_id")
            kick = db_session.query(UserModel).filter_by(UserModel.email == content["email"]).first()
            if kick is not None:
                circle = db_session.query(Circle).filter_by(Circle.id == content["circle_id"]).first()
                if circle is not None:
                    link = db_session.query(UserToCircle).filter(UserToCircle.user_id==kick.id, UserToCircle.circle_id==circle.id).first()
                    if link is not None:
                        db_session.delete(link)
                        db_session.commit()
                        return SUCCESS()
                    return FAILED("Lien entre utilisateur et cercle introuvable")
                return FAILED("Cercle spécifié introuvable")
            return FAILED("Utilisateur spécifié introuvable")
        except Exception as e:
            return FAILED(e)
