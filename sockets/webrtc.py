from config import socketio
from config.sockets import sockets
from config.turnserver import SECRET_KEY
from flask import request
from flask_socketio import emit
from utils.contentChecker import check_json
import time
import hmac
import hashlib


@socketio.on('webrtc_credentials')
def turn_auth(json):
    sid = request.sid
    try:
        socket = sockets.find_socket(sid)
        if socket is None or socket.authenticated is False:
            emit('error', 'Socket user introuvable', room=sid, namespace='/')
        else:
            unix_time = time.time()
            username = str(unix_time) + ':' + str(socket.client.id) + str(socket.is_device)
            digest_maker = hmac.new(SECRET_KEY, '', hashlib.sha1)
            digest_maker.update(username)
            password = digest_maker.digest()
            emit('webrtc_credentials', {username: username, password: password}, room=sid, namespace='/')
    except Exception as e:
        emit("error", str(e), room=sid, namespace='/')


@socketio.on('webrtc_forward')
def forward(json):
    pass


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
def stun_info(json):
    pass


@socketio.on('webrtc_turn_info')
def turn_info(json):
    pass
