from config import socketio, sockets
from flask import request
from flask_socketio import emit
from utils.log import logger_set
from config.log import LOG_SOCKET_FILE
from traceback import format_exc as traceback_format_exc

logger = logger_set(module=__name__, file=LOG_SOCKET_FILE)


@socketio.on("connect")
def connection():
    sockets.add(request.sid)
    logger.info("[%s] [%s] [%s] [%s]",
                "SOCKET", request.host, "connect", request.sid)


@socketio.on('authenticate')
def authenticate(content):
    sid = request.sid
    socket = sockets.find_socket(sid)
    try:
        if socket is None:
            raise Exception('Socket user introuvable')
        if 'token' not in content:
            raise Exception('Json web token introuvable')
        b, data = socket.authenticate(content['token'])
        if not b:
            raise Exception(data)
        socket.emit('success', data)
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", request.host, "authenticate", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "authenticate",
                       type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')


@socketio.on('disconnect')
def disconnection():
    sid = request.sid
    sockets.remove(sid)
    logger.info("[%s] [%s] [%s] [%s]",
                "SOCKET", request.host, "disconnect", request.sid)