from flask import request
from config.database import db
from models.User import User as UserModel
from models.Circle import Circle
from models.CircleInvite import CircleInvite as CircleInviteModel
from models.UserToCircle import UserToCircle
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_CIRCLE_FILE
from mobile import push_ios as ios

logger = logger_set(module=__name__, file=LOG_CIRCLE_FILE)


def invite(circle_id, email, client, is_device):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is not None:
            dest = db.session.query(UserModel).filter(UserModel.email == email).first()
            if dest is not None:
                if (not is_device and not circle.has_member(client)) or \
                        (is_device and circle_id != client.circle_id):
                    return FAILED("Utilisateur n'appartient pas au cercle spécifié", 403)
                if circle.has_member(dest) or circle.has_invite(dest):
                    return FAILED("Utilisateur fait déjà partie de ce cercle")
                circle_invite = CircleInviteModel()
                circle_invite.user = dest
                circle_invite.circle = circle
                db.session.commit()
                circle_invite.notify_user(p2={'event': 'invite', 'circle_id': circle.id})
                ios.send_notification(dest, "Invatation cercle " + circle.name)
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


def join(invite_id, user):
    try:
        invitation = db.session.query(CircleInviteModel).filter(CircleInviteModel.id == invite_id).first()
        if invitation is not None:
            if invitation.user_id != user.id:
                resp = FAILED("Action non authorisée", 403)
            else:
                link = UserToCircle(privilege="MEMBRE")
                link.user = invitation.user
                link.circle = invitation.circle
                db.session.delete(invitation)
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


def refuse_invite(invite_id, user):
    try:
        invitation = db.session.query(CircleInviteModel).filter(CircleInviteModel.id == invite_id).first()
        if invitation is not None:
            if invitation.user_id != user.id:
                resp = FAILED("Action non authorisée", 403)
            else:
                db.session.delete(invitation)
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


def quit_circle(circle_id, user):
    try:
        link = db.session.query(UserToCircle).filter(UserToCircle.circle_id == circle_id,
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


def kick_user(email, circle_id, user):
    try:
        kick = db.session.query(UserModel).filter(UserModel.email == email).first()
        if kick is not None:
            circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
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
