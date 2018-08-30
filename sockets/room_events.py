from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.UserToCircle import UserToCircle
from config.database import db
from config import socketio, sockets
from flask import request
from flask_socketio import join_room, leave_room, emit
from utils.log import logger_set
from config.log import LOG_SOCKET_FILE
from traceback import format_exc as traceback_format_exc

logger = logger_set(module=__name__, file=LOG_SOCKET_FILE)


@socketio.on('join_conversation')
def join_conversation_event(content):
    sid = request.sid
    socket = sockets.find_socket(sid)
    try:
        if socket is None or socket.authenticated is False:
            raise Exception('Socket user introuvable')
        client = socket.get_client()
        room = content['conversation_id']
        conversation = None
        conversation_link = None
        if socket.is_device:
            conversation = db.session.query(Conversation).filter(Conversation.id == room).first()
        else:
            conversation_link = db.session.query(UserToConversation).filter(
                UserToConversation.user_id == socket.client_id, UserToConversation.conversation_id == room).first()
        if (conversation is not None and conversation.circle_id == client.circle.id
                and conversation.device_access is True) or conversation_link is not None:
            join_room('conversation_' + str(room))
            socket.emit("success", "Vous avez rejoins la conversation : conversation_" +
                        str(content['conversation_id']))
        else:
            raise Exception("Vous ne faite pas partie de cette conversation")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", request.host, "join_conversation", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "join_conversation",
                       type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')
    db.session.close()


@socketio.on('join_circle')
def join_circle_event(content):
    sid = request.sid
    try:
        socket = sockets.find_socket(sid)
        if socket is None or socket.authenticated is False:
            raise Exception('Socket user introuvable, vous devez vous authentifier')
        else:
            client = socket.get_client()
            room = content['circle_id']
            if not socket.is_device:
                circle_link = db.session.query(UserToCircle).filter(UserToCircle.user_id == socket.client_id,
                                                                    UserToCircle.circle_id == room).first()
                if circle_link is not None:
                    join_room('circle_' + str(room))
                    socket.emit("success", "Vous avez rejoins le cercle : circle_" + str(content['circle_id']))
                else:
                    raise Exception("Vous n'appartenez pas a ce cercle")
            else:
                if client.circle_id == room:
                    join_room('circle_' + str(room))
                    socket.emit("success", "Vous avez rejoins le cercle : circle_" + str(content['circle_id']))
                else:
                    raise Exception("Vous n'appartenez pas a ce cercle")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", request.host, "join_circle", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "join_circle",
                       type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')
    db.session.close()


@socketio.on('leave_circle')
def leave_circle_event(content):
    sid = request.sid
    try:
        socket = sockets.find_socket(sid)
        if socket is None or socket.authenticated is False:
            raise Exception('Socket user introuvable')
        room = content['circle_id']
        leave_room('circle_' + str(room))
        socket.emit('success', "Vous avez quitte le cercle")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", request.host, "leave_circle", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "leave_circle",
                       type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')
    db.session.close()


@socketio.on('leave_conversation')
def leave_conversation_event(content):
    sid = request.sid
    try:
        socket = sockets.find_socket(sid)
        if socket is None or socket.authenticated is False:
            raise Exception('Socket user introuvable')
        room = content['conversation_id']
        leave_room('conversation_' + str(room))
        socket.emit('success', "Vous avez quitte la conversation")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", request.host, "leave_conversation", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "leave_conversation",
                       type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')
    db.session.close()
