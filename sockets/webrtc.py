from config import socketio
from config.sockets import sockets
from config.webrtc import STUN, TURN
from flask import request
from flask_socketio import emit
from utils.websocket import get_dest


@socketio.on('webrtc_credentials')
def turn_auth():
    sid = request.sid
    try:
        socket = sockets.find_socket(sid)
        if socket is None or socket.authenticated is False:
            emit('error', 'Socket user introuvable', room=sid, namespace='/')
        else:
            username, password = socket.generate_credentials()
            emit('webrtc_config', {"username": username, "password": password}, room=sid, namespace='/')
    except Exception as e:
        emit("error", str(e), room=sid, namespace='/')


@socketio.on('webrtc_forward')
def forward(json):
    sid = request.sid
    try:
        socket = sockets.find_socket(sid)
        if socket is None or socket.authenticated is False:
            emit('error', "Socket user introuvable", room=sid, namespace='/')
        else:
            is_device, dest = get_dest(json)
            if dest is None:
                raise Exception("Utilisateur introuvable")
            dest_socket = sockets.find_user(dest, is_device)
            if dest_socket is None:
                raise Exception("Destinataire non connecte aux websockets")
            dest_socket.emit("webrtc_forward", {
                "sender_id": socket.client_id,
                "is_device": socket.client.is_device,
                "content": json
            })
            socket.emit("success", "Message forwarded")
    except Exception as e:
        emit("error", str(e), room=sid, namespace='/')


@socketio.on('webrtc_join_room')
def join_room(json):
    pass


@socketio.on('webrtc_leave_room')
def leave_room(json):
    pass


@socketio.on('webrtc_room_forward')
def room_forward(json):
    pass


@socketio.on('webrtc_stun_info')
def stun_info():
    emit("webrtc_config", STUN, room=request.sid, namespace='/')


@socketio.on('webrtc_turn_info')
def turn_info():
    emit("webrtc_config", TURN, room=request.sid, namespace='/')
