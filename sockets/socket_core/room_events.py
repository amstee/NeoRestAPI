from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.UserToCircle import UserToCircle
from config.database import db
from flask_socketio import join_room, leave_room
from utils.log import logger_set
from config.log import LOG_SOCKET_FILE

logger = logger_set(module=__name__, file=LOG_SOCKET_FILE)


def join_conversation(room, socket):
    client = socket.get_client()
    conversation = None
    conversation_link = None
    if socket.is_device:
        conversation = db.session.query(Conversation).filter(Conversation.id == room).first()
    else:
        conversation_link = db.session.query(UserToConversation).filter(
            UserToConversation.user_id == socket.client_id, UserToConversation.conversation_id == room).first()
    if (conversation is not None and conversation.circle_id == client.circle.id and
            conversation.device_access is True) or conversation_link is not None:
        join_room('conversation_' + str(room))
        socket.emit("success", "Vous avez rejoins la conversation : conversation_" +
                    str(room))
    else:
        raise Exception("Vous ne faite pas partie de cette conversation")


def join_circle(room, socket):
    client = socket.get_client()
    if not socket.is_device:
        circle_link = db.session.query(UserToCircle).filter(UserToCircle.user_id == socket.client_id,
                                                            UserToCircle.circle_id == room).first()
        if circle_link is not None:
            join_room('circle_' + str(room))
            socket.emit("success", "Vous avez rejoins le cercle : circle_" + str(room))
        else:
            raise Exception("Vous n'appartenez pas a ce cercle")
    else:
        if client.circle_id == room:
            join_room('circle_' + str(room))
            socket.emit("success", "Vous avez rejoins le cercle : circle_" + str(room))
        else:
            raise Exception("Vous n'appartenez pas a ce cercle")


def leave_circle(room, socket):
    leave_room('circle_' + str(room))
    socket.emit('success', "Vous avez quitte le cercle")


def leave_conversation(room, socket):
    leave_room('conversation_' + str(room))
    socket.emit('success', "Vous avez quitte la conversation")
