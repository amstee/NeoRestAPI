from config.database import db
from config import socketio, sockets
from flask import request
from flask_socketio import emit
from utils.contentChecker import check_json
from utils.log import logger_set
from config.log import LOG_SOCKET_FILE
from traceback import format_exc as traceback_format_exc
from .socket_core.message_events import message_send, is_writing

logger = logger_set(module=__name__, file=LOG_SOCKET_FILE)


@socketio.on('writing')
def is_writing_event(content):
    sid = request.sid
    socket = sockets.find_socket(sid)
    try:
        if socket is None or socket.authenticated is False:
            raise Exception('Socket user introuvable')
        else:
            b, s = check_json(content, 'conversation_id', 'is_writing')
            if not b:
                raise Exception('Parameter missing')
            is_writing(content["conversation_id"], content["is_writing"], socket)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                        "SOCKET", request.host, "writing", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "writing", type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')
    db.session.close()


@socketio.on('message')
def message_send_event(content):
    sid = request.sid
    socket = sockets.find_socket(sid)
    try:
        if socket is None or socket.authenticated is False:
            raise Exception('Socket user introuvable')
        b, s = check_json(content, 'conversation_id')
        if not b:
            raise Exception('Param conversation_id introuvable')
        message_send(content["conversation_id"], content, socket)
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", request.host, "message", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "message", type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')
    db.session.close()
