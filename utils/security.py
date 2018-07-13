from config.database import db_session
from models.User import User
from models.Device import Device
from models.UserToConversation import UserToConversation


def getUserFromHeader(request):
    token = request.headers.get('Authorization')
    if token is None or token == "":
        raise Exception("Authorization token not found")
    res, data = User.decodeAuthToken(token)
    if res is True:
        return data
    raise Exception(data)


def getDeviceFromHeader(request):
    token = request.headers.get('Authorization')
    if token is None or token == "":
        raise Exception("Authorization token not found")
    res, data = Device.decodeAuthToken(token)
    if res is True:
        return data
    raise Exception(data)


def userHasAccessToMessage(message, user):
    if message.link is not None and message.link.user_id == user.id:
        return True
    link = db_session.query(UserToConversation).filter(UserToConversation.conversation_id==message.conversation_id,
                                                       UserToConversation.user_id==user.id).first()
    if link is None:
        return False
    return True


def userIsOwnerOfMessage(message, user):
    if message.link is None or message.isUser is False:
        return False
    if message.link.user_id==user.id:
        return True
    return False


def deviceHasAccessToMessage(message, device):
    if message.conversation.circle.device.id== device.id:
        if message.conversation.device_access is True:
            return True
    return False


def deviceIsOwnerOfMessage(message, device):
    if deviceHasAccessToMessage(message, device) and message.isUser is False:
        return True
    return False