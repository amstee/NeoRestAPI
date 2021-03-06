from config.database import db
from models.User import User
from models.Device import Device
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from .exceptions import InvalidAuthentication


def get_any_from_header(request):
    try:
        user = get_user_from_header(request)
        return user, False
    except InvalidAuthentication:
        return get_device_from_header(request), True


def get_user_from_header(request):
    token = request.headers.get('Authorization')
    if token is None or token == "":
        raise Exception("Authorization token not found")
    res, data = User.decode_auth_token_old(token)
    if res is True:
        return data
    raise InvalidAuthentication(data)


def get_device_from_header(request):
    token = request.headers.get('Authorization')
    if token is None or token == "":
        raise Exception("Authorization token not found")
    res, data = Device.decode_auth_token_old(token)
    if res is True:
        return data
    raise InvalidAuthentication(data)


def user_has_access_to_message(message, user):
    if message.link is not None and message.link.user_id == user.id:
        return True
    link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id == message.conversation_id,
                                                       UserToConversation.user_id == user.id).first()
    if link is None:
        return False
    return True


def user_has_access_to_media(media, user):
    if media.directory is None or media.directory == "":
        return False
    data = media.directory.split("_")
    if len(data) == 2:
        type = data[0]
        id = data[1]
        if type == "conversation":
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id == id,
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                return False
    return True


def user_is_owner_of_message(message, user):
    if message.link is None or message.is_user is False:
        return False
    if message.link.user_id == user.id:
        return True
    return False


def device_has_access_to_message(message, device):
    if message.conversation.circle.device.id == device.id:
        if message.conversation.device_access is True:
            return True
    return False


def device_has_access_to_media(media, device):
    if media.directory is None or media.directory == "":
        return False
    data = media.directory.split("_")
    if len(data) == 2:
        type = data[0]
        id = data[1]
        if type == "conversation":
            link = db.session.query(Conversation).filter(Conversation.device_access is True,
                                                         Conversation.circle_id == device.circle_id,
                                                         Conversation.id == id).first()
            if link is None:
                return False
    return True


def device_is_owner_of_message(message, device):
    if device_has_access_to_message(message, device) and message.is_user is False:
        return True
    return False
