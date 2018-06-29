from models.UserToConversation import UserToConversation
from models.UserToCircle import UserToCircle
from config.database import db_session
from config import socketio, sockets
from flask import request
from flask_socketio import join_room, leave_room, emit

@socketio.on('join_conversation_event')
def join_conversation_event(json):
    sid = request.sid
    socket = sockets.find_socket(sid)
    if socket is None:
        emit('error', 'Socket user introuvable', room=sid)
    else:
        try:
            room = json['conversation_id']
            conversation_link = db_session.query(UserToConversation).filter(UserToConversation.user_id == socket.user.id, UserToConversation.conversation_id == room).first()
            if conversation_link is not None:
                join_room('conversation_' + str(room))
                socket.emit("success", "Vous avez rejoins la conversation : conversation_" + str(json['conversation_id']))
            else:
                socket.emit("error", "Vous ne faite pas partie de cette conversation")
        except Exception as e:
            socket.emit("error", str(e))


@socketio.on('join_circle_event')
def join_circle_event(json):
    try:
        sid = request.sid
        socket = sockets.find_socket(sid)
        if socket is None:
            emit('error', 'Socket user introuvable, vous devez vous authentifier', room=sid, namespace='/')
        else:
            room = json['circle_id']
            circle_link = db_session.query(UserToCircle).filter(UserToCircle.user_id == socket.user.id, UserToCircle.circle_id == room).first()
            if circle_link is not None:
                join_room('circle_' + str(room))
                socket.emit("success", "Vous avez rejoins le cercle : circle_" + str(json['circle_id']))
            else:
                socket.emit("error", "Vous ne faites pas partie de ce cercle")
    except Exception as e:
        emit('error', str(e), namespace='/')


@socketio.on('leave_circle_event')
def leave_circle_event(json):
    try:
        sid = request.sid
        socket = sockets.find_socket(sid)
        if socket is None:
            emit('error', 'Socket user introuvable', room=sid, namespace='/')
        else:
            room = json['circle_id']
            leave_room('circle_' + str(room))
    except Exception as e:
        emit('error', str(e), namespace='/')


@socketio.on('leave_conversation_event')
def leave_conversation_event(json):
    sid = request.sid
    socket = sockets.find_socket(sid)
    if socket is None:
        emit('error', 'Socket user introuvable', room=sid, namespace='/')
    else:
        try:
            room = json['conversation_id']
            leave_room('conversation_' + str(room))
        except Exception as e:
            socket.emit("error", str(e))