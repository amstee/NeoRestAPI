from flask_restful import Resource
from config.database import db
from models.User import User as UserModel
from models.Circle import Circle
from models.CircleInvite import CircleInvite as CircleInviteModel
from utils.decorators import secured_route, check_content
from models.UserToCircle import UserToCircle
from utils.contentChecker import content_checker
from utils.apiUtils import *


class CircleInvite(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("circle_id", "email")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is not None:
                dest = db.session.query(UserModel).filter(UserModel.email == content["email"]).first()
                if dest is not None:
                    if not circle.has_member(user):
                        return FAILED("Utilisateur n'appartient pas au cercle spécifié", 403)
                    if circle.has_member(dest) or circle.has_invite(dest):
                        return FAILED("Utilisateur fait déjà partie de ce cercle")
                    circle_invite = CircleInviteModel()
                    circle_invite.user = dest
                    circle_invite.circle = circle
                    db.session.commit()
                    circle_invite.notify_user(p2={'event': 'invite', 'circle_id': circle.id})
                    return SUCCESS()
                return FAILED("Utilisateur spécifié introuvable")
            return FAILED("Cercle spécifié introuvable")
        except Exception as e:
            return FAILED(e)


class CircleJoin(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("invite_id")
            invite = db.session.query(CircleInviteModel).filter(CircleInviteModel.id == content["invite_id"]).first()
            if invite is not None:
                if invite.user_id != user.id:
                    return FAILED("Action non authorisée", 403)
                link = UserToCircle(privilege="MEMBRE")
                link.user = invite.user
                link.circle = invite.circle
                db.session.delete(invite)
                db.session.commit()
                link.circle.notify_users(p1='circle', p2={'event': 'join', 'user': link.user.email})
                return SUCCESS()
            return FAILED("Invitation introuvable")
        except Exception as e:
            return FAILED(e)


class CircleReject(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("invite_id")
            invite = db.session.query(CircleInviteModel).filter(CircleInviteModel.id == content["invite_id"]).first()
            if invite is not None:
                if invite.user_id != user.id:
                    return FAILED("Action non authorisée", 403)
                db.session.delete(invite)
                return SUCCESS()
            return FAILED("Invitation introuvable")
        except Exception as e:
            return FAILED(e)


class CircleQuit(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            link = db.session.query(UserToCircle).filter(UserToCircle.circle_id == content["circle_id"],
                                                         UserToCircle.user_id == user.id).first()
            if link is not None:
                id_circle = link.circle.id
                link.circle.notify_users('circle', {'event': 'quit', 'user': link.user.email})
                db.session.delete(link)
                db.session.commit()
                circle = db.session.query(Circle).filter(Circle.id == id_circle).first()
                circle.check_validity()
                return SUCCESS()
            return FAILED("L'utilisateur n'appartient pas a ce cercle", 403)
        except Exception as e:
            return FAILED(e)


class CircleKick(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("email", "circle_id")
            kick = db.session.query(UserModel).filter(UserModel.email == content["email"]).first()
            if kick is not None:
                circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
                if circle is not None:
                    link = db.session.query(UserToCircle).filter(UserToCircle.user_id == kick.id,
                                                                 UserToCircle.circle_id == circle.id).first()
                    if link is not None:
                        db.session.delete(link)
                        db.session.commit()
                        circle.notify_users('circle', {'event': 'kick', 'user': kick.email, 'from': user.email})
                        return SUCCESS()
                    return FAILED("Lien entre utilisateur et cercle introuvable")
                return FAILED("Cercle spécifié introuvable")
            return FAILED("Utilisateur spécifié introuvable")
        except Exception as e:
            return FAILED(e)
