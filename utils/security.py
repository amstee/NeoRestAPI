from config.database import db_session
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation

def userHasAccessToMessage(message, user):
    if message.link is None:
        return False
    if message.link.user_id == user.id:
        return True
    link = db_session.query(UserToConversation).join(Conversation).filter(Conversation.id==message.link.conversation_id, UserToConversation.user_id==user.id).first()
    if link is None:
        return False
    return True

def userIsOwnerOfMessage(message, user):
    if message.link is None:
        return False
    if message.link.user_id==user.id:
        return True
    return False