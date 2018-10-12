from config.database import db
from models.Circle import Circle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from exceptions import conversation as e_conversation
from exceptions import circle as e_circle


def update(content, conversation_id, client, is_device):
    try:
        if not is_device:
            link = db.session.query(UserToConversation).filter(UserToConversation.user_id == client.id,
                                                               UserToConversation.conversation_id ==
                                                               conversation_id).first()
            if link is None:
                raise e_conversation.UserForbiddenAccess
            if link.privilege != "ADMIN":
                raise e_conversation.InsufficientRight
            link.conversation.update_content(name=content["conversation_name"] if "conversation_name"
                                                                                  in content else None,
                                             created=content["created"] if "created" in content else None,
                                             device_access=content["device_access"] if "device_access"
                                                                                       in content else None)
            link.conversation.notify_users(p2={'event': 'update'})
            response = {
                "data": {"success": True, "content": link.conversation.get_simple_content()},
                "status_code": 200
            }
        else:
            conversation = db.session.query(Conversation).filter(Conversation.device_access is True,
                                                                 Conversation.circle_id == client.circle_id).first()
            if conversation is None:
                raise e_conversation.UserForbiddenAccess
            conversation.update_content(name=content["conversation_name"] if "conversation_name"
                                                                             in content else None,
                                        created=content["created"] if "created" in content else None,
                                        device_access=content["device_access"] if "device_access"
                                                                                  in content else None)
            conversation.notify_users(p2={'event': 'update'})
            response = {
                "data": {"success": True, "content": conversation.get_simple_content()},
                "status_code": 200
            }
    except e_conversation.ConversationException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def conversation_list(circle_id, client, is_device):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            raise e_circle.CircleNotFound
        if (not is_device and not circle.has_member(client) or
              (is_device and circle.device_id != client.id)):
            raise e_circle.UserNotPartOfCircle
        if not is_device:
            conversations = db.session.query(Conversation).join(UserToConversation).filter(
                Conversation.circle_id == circle.id,
                UserToConversation.user_id == client.id
            ).all()
        else:
            conversations = db.session.query(Conversation).filter(Conversation.device_access is True,
                                                                  Conversation.circle_id == client.circle_id).all()
        response = {
            "data": {"success": True, "content": [conversation.get_simple_content() for conversation in conversations]},
            "status_code": 200
        }
    except (e_conversation.ConversationException, e_circle.CircleException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def info(conversation_id, client, is_device):
    try:
        conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation is None:
            raise e_conversation.ConversationNotFound
        if (not is_device and not conversation.has_members(client)) or \
                (is_device and not (conversation.device_access and conversation.circle_id == client.circle_id)):
            raise e_conversation.UserForbiddenAccess
        response = {
            "data": {"success": True, "content": conversation.get_content()},
            "status_code": 200
        }
    except e_conversation.ConversationException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def admin_create(name, circle_id):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            raise e_circle.CircleNotFound
        conversation = Conversation(name=name)
        conversation.circle = circle
        db.session.commit()
        response = {
            "data": {"success": True, "content": conversation.get_simple_content()},
            "status_code": 200
        }
    except (e_conversation.ConversationException, e_circle.CircleException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def admin_delete(conversation_id):
    try:
        conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation is None:
            raise e_conversation.ConversationNotFound
        db.session.delete(conversation)
        db.session.commit()
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
