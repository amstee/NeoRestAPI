from flask_restful import Resource
from config.database import db_session
from models.User import User as UserModel
from models.Circle import Circle
from models.CircleInvite import CircleInvite as CircleInviteModel
from utils.decorators import securedRoute, checkContent
from models.UserToCircle import UserToCircle
from utils.contentChecker import contentChecker
from config.sockets import sockets
from utils.apiUtils import *


class CircleInvite(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("circle_id", "email")
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            if circle is not None:
                dest = db_session.query(UserModel).filter(UserModel.email == content["email"]).first()
                if dest is not None:
                    if not circle.hasMember(user):
                        return FAILED("Utilisateur n'appartient pas au cercle spécifié", 403)
                    if circle.hasMember(dest) or circle.hasInvite(dest):
                        return FAILED("Utilisateur fait déjà partie de ce cercle")
# if not circle.hasAdmin(user):
#     return FAILED("Utilisateur n'a pas les privileges necessaires", 403)
                    circle_invite = CircleInviteModel()
                    circle_invite.user = dest
                    circle_invite.circle = circle
                    db_session.commit()
                    circle_invite.notify_user(p2={'event': 'invite', 'circle_id': circle.id})
                    return SUCCESS()
                return FAILED("Utilisateur spécifié introuvable")
            return FAILED("Cercle spécifié introuvable")
        except Exception as e:
            return FAILED(e)


class CircleJoin(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("invite_id")
            invite = db_session.query(CircleInviteModel).filter(CircleInviteModel.id == content["invite_id"]).first()
            if invite is not None:
                if invite.user_id != user.id:
                    return FAILED("Action non authorisée", 403)
                link = UserToCircle(privilege="MEMBRE")
                link.user = invite.user
                link.circle = invite.circle
                db_session.delete(invite)
                db_session.commit()
                link.circle.notify_users(p1='circle', p2={'event': 'join', 'user': link.user.email})
                return SUCCESS()
            return FAILED("Invitation introuvable")
        except Exception as e:
            return FAILED(e)


class CircleReject(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("invite_id")
            invite = db_session.query(CircleInviteModel).filter(CircleInviteModel.id == content["invite_id"]).first()
            if invite is not None:
                if invite.user_id != user.id:
                    return FAILED("Action non authorisée", 403)
                db_session.delete(invite)
                return SUCCESS()
            return FAILED("Invitation introuvable")
        except Exception as e:
            return FAILED(e)


class CircleQuit(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("circle_id")
            link = db_session.query(UserToCircle).filter(UserToCircle.circle_id==content["circle_id"],
                                                         UserToCircle.user_id==user.id).first()
            if link is not None:
                id = link.circle.id
                link.circle.notify_users('circle', {'event': 'quit', 'user': link.user.email})
                db_session.delete(link)
                db_session.commit()
                circle = db_session.query(Circle).filter(Circle.id == id).first()
                circle.checkValidity()
                return SUCCESS()
            return FAILED("L'utilisateur n'appartient pas a ce cercle", 403)
        except Exception as e:
            return FAILED(e)


class CircleKick(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("email", "circle_id")
            kick = db_session.query(UserModel).filter(UserModel.email == content["email"]).first()
            if kick is not None:
                circle = db_session.query(Circle).filter(Circle.id == content["circle_id"]).first()
                if circle is not None:
                    link = db_session.query(UserToCircle).filter(UserToCircle.user_id==kick.id, UserToCircle.circle_id==circle.id).first()
                    if link is not None:
                        db_session.delete(link)
                        db_session.commit()
                        circle.notify_users('circle', {'event': 'kick', 'user': kick.email, 'from': user.email})
                        return SUCCESS()
                    return FAILED("Lien entre utilisateur et cercle introuvable")
                return FAILED("Cercle spécifié introuvable")
            return FAILED("Utilisateur spécifié introuvable")
        except Exception as e:
            return FAILED(e)
