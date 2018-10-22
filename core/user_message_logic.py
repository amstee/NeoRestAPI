from config.database import db
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.Media import Media
from models.Message import Message
from models.Circle import Circle
from models.User import User as UserModel
from models.MessageToMedia import MessageToMedia
from config.sockets import sockets
from flask_socketio import emit
from bot.facebook import messenger_conversation_model_send
from bot.hangout import hangout_conversation_model_send
from exceptions import conversation as e_conversation
from exceptions import circle as e_circle
from exceptions import message as e_message


def message_send(content, conversation_id, user):
    try:
        link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
                                                           UserToConversation.user_id == user.id).first()
        if link is None:
            raise e_conversation.ConversationNotFound
        message = Message(content=content["text_message"] if "text_message" in content else "")
        message.conversation = link.conversation
        message.link = link
        media_list = []
        if "files" in content:
            for file in content["files"]:
                media = Media()
                media.identifier = file
                MessageToMedia(message=message, media=media)
                db.session.commit()
                media_list.append(media.get_simple_content())
        db.session.commit()
        if not media_list:
            emit('message', {
                'conversation_id': message.conversation_id,
                'message': message.get_simple_json_compliant_content(),
                'time': message.sent.isoformat(),
                'sender': user.get_simple_json_compliant_content(),
                'media_list': media_list,
                'status': 'done'},
                 room='conversation_' + str(message.conversation_id), namespace='/')
        else:
            emit('message', {'conversation_id': message.conversation_id,
                             'message': message.get_simple_json_compliant_content(),
                             'status': 'pending'}, room='conversation_' + str(message.conversation_id),
                 namespace='/')
        message.conversation.mobile_notification("Nouveau message de %s" % user.email)
        conversation = db.session.query(Conversation).filter(link.conversation_id == Conversation.id).first()
        info_sender = "[" + link.conversation.name + "] " + user.first_name + " : "
        try:
            messenger_conversation_model_send(link.user_id, conversation, info_sender + message.text_content)
        except Exception:
            pass
        try:
            hangout_conversation_model_send(link.user_id, conversation, info_sender + message.text_content)
        except Exception:
            pass
        response = {
            "data": {"success": True, 'media_list': media_list, 'message_id': message.id},
            "status_code": 200
        }
    except e_conversation.ConversationException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def first_message_to_user(content, email, circle_id, user):
    try:
        dest = db.session.query(UserModel).filter(UserModel.email == email).first()
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if dest is None:
            raise e_message.TargetUserNotFound
        if circle is None:
            raise e_circle.CircleNotFound
        if not circle.has_member(user):
            raise e_circle.UserNotPartOfCircle
        if not circle.has_member(dest) and circle.has_member(user):
            raise e_circle.TargetUserNotPartOfCircle
        conversation = Conversation()
        conversation.circle = circle
        UserToConversation(privilege="ADMIN", user=user, conversation=conversation)
        UserToConversation(privilege="STANDARD", user=dest, conversation=conversation)
        message = Message(content=content["text_message"] if "text_message" in content else "")
        message.conversation = conversation
        media_list = []
        if "files" in content:
            for file in content["files"]:
                media = Media()
                media.identifier = file
                MessageToMedia(message=message, media=media)
                db.session.commit()
                media_list.append(media.get_simple_content())
        db.session.commit()
        sockets.notify_user(dest, False, 'conversation',
                            {"conversation_id": conversation.id,
                             "event": 'invite'})
        info_sender = "[" + conversation.name + "] " + user.first_name + " : "
        try:
            messenger_conversation_model_send(user.id, conversation, info_sender + message.text_content)
        except Exception:
            pass
        try:
            hangout_conversation_model_send(user.id, conversation, info_sender + message.text_content)
        except Exception:
            pass
        response = {
            "data": {"success": True, 'media_list': media_list, 'message_id': message.id,
                     'conversation_id': message.conversation_id},
            "status_code": 200
        }
    except (e_message.MessageException, e_circle.CircleException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def first_message_to_device(content, circle_id, user):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            raise e_circle.CircleNotFound
        elif not circle.has_member(user):
            raise e_circle.UserNotPartOfCircle
        conversation = Conversation(name=content["conversation_name"] if "conversation_name" in content else
                                    circle.name, device_access=True)
        conversation.circle = circle
        link = UserToConversation(privilege="ADMIN")
        link.user = user
        link.conversation = conversation
        message = Message(content=content["text_message"] if "text_message" in content else "")
        message.conversation = conversation
        message.link = link
        media_list = []
        if "files" in content:
            for file in content["files"]:
                media = Media()
                media.identifier = file
                MessageToMedia(message=message, media=media)
                db.session.commit()
                media_list.append(media.get_simple_content())
        db.session.commit()
        sockets.notify_user(circle.device, True, 'conversation',
                            {"conversation_id": conversation.id,
                             "event": 'invite'})
        info_sender = "[" + conversation.name + "] " + user.first_name + " : "
        try:
            messenger_conversation_model_send(user.id, conversation, info_sender + message.text_content)
        except Exception:
            pass
        try:
            hangout_conversation_model_send(user.id, conversation, info_sender + message.text_content)
        except Exception:
            pass
        response = {
            "data": {"success": True, 'media_list': media_list, 'message_id': message.id},
            "status_code": 200
        }
    except (e_message.MessageException, e_circle.CircleException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response
