import traceback
from config import socketio
from config.sockets import sockets
from flask import request
from flask_socketio import emit
from .socket_core import webrtc_events


@socketio.on('webrtc_credentials')
def get_credentials_event():
    sid = request.sid
    try:
        socket = sockets.find_socket(sid)
        if socket is None or socket.authenticated is False:
            emit('error', 'Socket user introuvable', room=sid, namespace='/')
        else:
            webrtc_events.get_credentials(socket, sid)
    except Exception as e:
        traceback.print_exc()
        emit("error", str(e), room=sid, namespace='/')


@socketio.on('webrtc_forward')
def forward_event(json):
    sid = request.sid
    try:
        socket = sockets.find_socket(sid)
        if socket is None or socket.authenticated is False:
            emit('error', "Socket user introuvable", room=sid, namespace='/')
        else:
            webrtc_events.forward_message(json, socket)
    except Exception as e:
        emit("error", str(e), room=sid, namespace='/')


@socketio.on('webrtc_join_room')
def join_room_event(json):
    webrtc_events.join_room()


@socketio.on('webrtc_leave_room')
def leave_room_event(json):
    webrtc_events.leave_room()


@socketio.on('webrtc_room_forward')
def room_forward_event(json):
    webrtc_events.room_forward()


@socketio.on('webrtc_stun_info')
def stun_inf_evento():
    webrtc_events.stun_info(request.sid)


@socketio.on('webrtc_turn_info')
def turn_info_event():
    webrtc_events.turn_info(request.sid)
