from config.sockets import sockets
from config.webrtc import STUN, TURN
from flask_socketio import emit
from utils.websocket import get_dest


def get_credentials(socket, sid):
    username, password = socket.generate_credentials()
    emit('webrtc_config', {"username": username, "password": password}, room=sid, namespace='/')


def forward_message(json_data, socket):
    is_device, dest = get_dest(json_data)
    if dest is None:
        raise Exception("Utilisateur introuvable")
    dest_socket = sockets.find_user(dest, is_device)
    if dest_socket is None:
        raise Exception("Destinataire non connecte aux websockets")
    dest_socket.emit("webrtc_forward", {
        "sender_id": socket.client_id,
        "is_device": socket.is_device,
        "content": json_data
    })
    socket.emit("success", "Message forwarded")


def join_room():
    pass


def leave_room():
    pass


def room_forward():
    pass


def stun_info(sid):
    emit("webrtc_config", STUN, room=sid, namespace='/')


def turn_info(sid):
    emit("webrtc_config", TURN, room=sid, namespace='/')
