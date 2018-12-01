from flask import request
from config.database import db
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.User import User as UserModel
from config.sockets import sockets
from exceptions import conversation as e_conversation
from exceptions import circle as e_circle


def set_device(conversation_id, client, is_device):
    try:
        privilege = ""
        if not is_device:
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               conversation_id,
                                                               UserToConversation.user_id == client.id).first()
            if link is None:
                raise e_conversation.UserForbiddenAccess
            conversation = link.conversation
            privilege = link.privilege
        else:
            conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation is None:
            raise e_conversation.ConversationNotFound
        if privilege != "ADMIN" and not (is_device and conversation.device_access):
            raise e_conversation.InsufficientRight
        if privilege == "ADMIN":
            conversation.update_content(device_access=(not conversation.device_access))
            if conversation.device_access:
                conversation.notify_users(p2={'event': 'device', 'type': 'add'})
            else:
                conversation.notify_users(p2={'event': 'device', 'type': 'remove'})
        elif is_device and conversation.device_access:
            conversation.update_content(device_access=False)
            conversation.notify_users(p2={'event': 'device', 'type': 'remove'})
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_conversation.ConversationException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def invite(conversation_id, email, client, is_device):
    try:
        if not is_device:
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               conversation_id,
                                                               UserToConversation.user_id == client.id).first()
            if link is None:
                raise e_conversation.UserForbiddenAccess
            conversation = link.conversation
        else:
            conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation is None:
            raise e_conversation.ConversationNotFound
        recipient = db.session.query(UserModel).filter(UserModel.email == email).first()
        if recipient is None:
            raise e_conversation.SpecifiedUserNotFound
        temp = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
                                                           UserToConversation.user_id == recipient.id).first()
        if temp is not None:
            raise e_conversation.UserAlreadyPartOfConversation
        if not conversation.circle.has_member(recipient):
            raise e_circle.UserNotPartOfCircle
        new_link = UserToConversation(privilege="STANDARD")
        new_link.user = recipient
        new_link.conversation = conversation
        db.session.commit()
        #.conversation.mobile_notification(title="Invitation", body="Vous êtes invité dans un nouveau cercle.")
        sockets.notify_user(client=recipient, is_device=False, p1='conversation',
                            p2={'event': 'invite', 'conversation_id': conversation_id})
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except (e_conversation.ConversationException, e_circle.CircleException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def conversation_quit(conversation_id, user):
    try:
        link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
                                                           UserToConversation.user_id == user.id).first()
        if link is None:
            raise e_conversation.UserForbiddenAccess
        conversation = link.conversation
        if link.user_id == user.id:
            conversation.notify_users(p2={'event': 'quit', 'user': user.email})
            db.session.delete(link)
            db.session.commit()
        if conversation.check_validity():
            conversation.set_other_admin()
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_conversation.ConversationException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def conversation_kick(conversation_id, email, user):
    try:
        link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
                                                           UserToConversation.user_id == user.id).first()
        if link is None:
            raise e_conversation.UserForbiddenAccess
        recipient = db.session.query(UserModel).filter(UserModel.email == email).first()
        if recipient is None:
            raise e_conversation.SpecifiedUserNotFound
        temp = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           link.conversation_id,
                                                           UserToConversation.user_id == recipient.id).first()
        if temp is None:
            raise e_conversation.TargetUserNotPartOfConversation
        if link.privilege != "ADMIN":
            raise e_conversation.InsufficientRight
        db.session.delete(temp)
        db.session.commit()
        link.conversation.check_validity()
        link.conversation.notify_users(p2={'event': 'kick', 'user': recipient.email, 'from': user.email})
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_conversation.ConversationException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def user_promote(conversation_id, email, user):
    try:
        link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
                                                           UserToConversation.user_id == user.id).first()
        if link is None:
            raise e_conversation.UserForbiddenAccess
        recipient = db.session.query(UserModel).filter(UserModel.email == email).first()
        if recipient is None:
            raise e_conversation.SpecifiedUserNotFound
        temp = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           link.conversation_id,
                                                           UserToConversation.user_id == recipient.id).first()
        if temp is None:
            raise e_conversation.TargetUserNotPartOfConversation
        if link.privilege != "ADMIN":
            raise e_conversation.InsufficientRight
        temp.update_content(privilege="ADMIN")
        link.update_content(privilege="STANDARD")
        sockets.notify_user(client=recipient, is_device=False, p1='conversation',
                            p2={'event': 'promoted', 'conversation_id': link.conversation_id})

        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_conversation.ConversationException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response
