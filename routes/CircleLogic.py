from flask_restful import Resource
from flask import request
from config.database import db
from models.User import User as UserModel
from models.Circle import Circle
from models.CircleInvite import CircleInvite as CircleInviteModel
from utils.decorators import secured_route, check_content
from models.UserToCircle import UserToCircle
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_CIRCLE_FILE

logger = logger_set(module=__name__, file=LOG_CIRCLE_FILE)


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
                    resp = SUCCESS()
                else:
                    resp = FAILED("Utilisateur spécifié introuvable")
            else:
                resp = FAILED("Cercle spécifié introuvable")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class CircleJoin(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("invite_id")
            invite = db.session.query(CircleInviteModel).filter(CircleInviteModel.id == content["invite_id"]).first()
            if invite is not None:
                if invite.user_id != user.id:
                    resp = FAILED("Action non authorisée", 403)
                else:
                    link = UserToCircle(privilege="MEMBRE")
                    link.user = invite.user
                    link.circle = invite.circle
                    db.session.delete(invite)
                    db.session.commit()
                    link.circle.notify_users(p1='circle', p2={'event': 'join', 'user': link.user.email})
                    resp = SUCCESS()
            else:
                resp = FAILED("Invitation introuvable")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class CircleReject(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("invite_id")
            invite = db.session.query(CircleInviteModel).filter(CircleInviteModel.id == content["invite_id"]).first()
            if invite is not None:
                if invite.user_id != user.id:
                    resp = FAILED("Action non authorisée", 403)
                else:
                    db.session.delete(invite)
                    db.session.commit()
                    resp = SUCCESS()
            else:
                resp = FAILED("Invitation introuvable")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


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
                resp = SUCCESS()
            else:
                resp = FAILED("L'utilisateur n'appartient pas a ce cercle", 403)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


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
                        resp = SUCCESS()
                    else:
                        resp = FAILED("Lien entre utilisateur et cercle introuvable")
                else:
                    resp = FAILED("Cercle spécifié introuvable")
            else:
                resp = FAILED("Utilisateur spécifié introuvable")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp
