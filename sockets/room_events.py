from models.UserToConversation import UserToConversation
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
            conversation_link = db_session.query(UserToConversation).filter(UserToConversation.user_id == socket.user.id and UserToConversation.conversation_id == room).first()
            if conversation_link is not None:
                join_room(str(room))
                socket.emit("success", "Vous avez rejoins la conversation " + str(json['conversation_id']))
            else:
                socket.emit("error", "Vous ne faite pas partie de cette conversation")
        except Exception as e:
            socket.emit("error", str(e))

@socketio.on('leave_conversation_event')
def leave_conversation_event(json):
    sid = request.sid
    socket = sockets.find_socket(sid)
    if socket is None:
        emit('error', 'Socket user introuvable', room=sid)
    else:
        try:
            room = json['conversation_id']
            leave_room(str(room))
        except Exception as e:
            socket.emit("error", str(e))