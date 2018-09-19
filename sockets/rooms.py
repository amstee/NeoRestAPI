from config.database import db
from config import socketio, sockets
from flask import request
from utils.contentChecker import check_json
from flask_socketio import emit
from utils.log import logger_set
from config.log import LOG_SOCKET_FILE
from traceback import format_exc as traceback_format_exc
from .socket_core import room_events

logger = logger_set(module=__name__, file=LOG_SOCKET_FILE)


@socketio.on('join_conversation')
def join_conversation_event(content):
    sid = request.sid
    socket = sockets.find_socket(sid)
    try:
        if socket is None or socket.authenticated is False:
            raise Exception('Socket user introuvable')
        b, s = check_json(content, 'conversation_id')
        if not b:
            raise Exception('Parameter missing')
        room_events.join_conversation(content["conversation_id"], socket)
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
        b, s = check_json(content, 'circle_id')
        if not b:
            raise Exception('Parameter missing')
        room_events.join_circle(content["circle_id"], socket)
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
        b, s = check_json(content, 'circle_id')
        if not b:
            raise Exception('Parameter circle_id missing')
        room_events.leave_circle(content["circle_id"], socket)
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
        b, s = check_json(content, 'conversation_id')
        if not b:
            raise Exception('Parameter conversation_id missing')
        room_events.leave_conversation(content["conversation_id"], socket)
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", request.host, "leave_conversation", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "leave_conversation",
                       type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')
    db.session.close()
