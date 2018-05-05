from config.database import db_session
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.Device import Device

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
    if message.conversation.circle.device_id == device.id:
        if message.conversation.device_access is True:
            return True
    return False
