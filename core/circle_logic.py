from config.database import db
from models.User import User as UserModel
from models.Circle import Circle
from models.CircleInvite import CircleInvite as CircleInviteModel
from models.UserToCircle import UserToCircle
from exceptions import circle as e_circle
from mobile import push_ios as ios


def invite(circle_id, email, client, is_device):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            raise e_circle.CircleNotFound
        dest = db.session.query(UserModel).filter(UserModel.email == email).first()
        if dest is None:
            raise e_circle.InvitedUserNotFound
        if (not is_device and not circle.has_member(client)) or \
                (is_device and circle_id != client.circle_id):
            raise e_circle.UserForbiddenAccess
        if circle.has_member(dest) or circle.has_invite(dest):
            return e_circle.UserAlreadyPartOfCircle
        circle_invite = CircleInviteModel()
        circle_invite.user = dest
        circle_invite.circle = circle
        db.session.commit()
        circle_invite.notify_user(p2={'event': 'invite', 'circle_id': circle.id})
        ios.send_notification(dest, "Invitation cercle " + circle.name)
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_circle.CircleException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def join(invite_id, user):
    try:
        invitation = db.session.query(CircleInviteModel).filter(CircleInviteModel.id == invite_id).first()
        if invitation is None:
            raise e_circle.InvitationNotFound
        if invitation.user_id != user.id:
            raise e_circle.UnallowedToUseInvitation
        link = UserToCircle(privilege="MEMBRE")
        link.user = invitation.user
        link.circle = invitation.circle
        db.session.delete(invitation)
        db.session.commit()
        link.circle.notify_users(p1='circle', p2={'event': 'join', 'user': link.user.email})
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_circle.CircleException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def refuse_invite(invite_id, user):
    try:
        invitation = db.session.query(CircleInviteModel).filter(CircleInviteModel.id == invite_id).first()
        if invitation is None:
            raise e_circle.InvitationNotFound
        if invitation.user_id != user.id:
            raise e_circle.UnallowedToUseInvitation
        db.session.delete(invitation)
        db.session.commit()
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_circle.CircleException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def quit_circle(circle_id, user):
    try:
        link = db.session.query(UserToCircle).filter(UserToCircle.circle_id == circle_id,
                                                     UserToCircle.user_id == user.id).first()
        if link is None:
            raise e_circle.UserNotPartOfCircle
        id_circle = link.circle.id
        link.circle.notify_users('circle', {'event': 'quit', 'user': link.user.email})
        db.session.delete(link)
        db.session.commit()
        circle = db.session.query(Circle).filter(Circle.id == id_circle).first()
        circle.check_validity()
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_circle.CircleException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def kick_user(email, circle_id, user):
    try:
        kick = db.session.query(UserModel).filter(UserModel.email == email).first()
        if kick is None:
            raise e_circle.TargetUserNotPartOfCircle
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            raise e_circle.CircleNotFound
        link = db.session.query(UserToCircle).filter(UserToCircle.user_id == kick.id,
                                                     UserToCircle.circle_id == circle.id).first()
        if link is None:
            raise e_circle.TargetUserNotPartOfCircle
        db.session.delete(link)
        db.session.commit()
        circle.notify_users('circle', {'event': 'kick', 'user': kick.email, 'from': user.email})
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_circle.CircleException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response
