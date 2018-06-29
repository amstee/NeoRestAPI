from config import socketio, sockets
from flask import request
from flask_socketio import emit


@socketio.on("connect")
def connection():
    sockets.add(request.sid)


@socketio.on('authenticate')
def authenticate(json):
    sid = request.sid
    socket = sockets.find_socket(sid)
    if socket is None:
        emit('error', 'Socket user introuvable', room=sid, namespace='/')
    if 'token' not in json:
        socket.emit('error', 'Json web token introuvable')
    b, data = socket.authenticate(json['token'])
    if not b:
        socket.emit('error', data)
    else:
        socket.emit('success', data)


@socketio.on('disconnect')
def disconnection():
    sid = request.sid
    sockets.remove(sid)
