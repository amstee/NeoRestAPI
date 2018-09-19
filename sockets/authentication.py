from config import socketio
from flask import request
from flask_socketio import emit
from utils.log import logger_set
from config.log import LOG_SOCKET_FILE
from traceback import format_exc as traceback_format_exc
from .socket_core import authentication_events

logger = logger_set(module=__name__, file=LOG_SOCKET_FILE)


@socketio.on("connect")
def connection_event():
    logger.info("[%s] [%s] [%s] [%s]",
                "SOCKET", request.host, "connect", request.sid)


@socketio.on('authenticate')
def authenticate_event(content):
    sid = request.sid
    try:
        if 'token' not in content:
            raise Exception('Json web token introuvable')
        authentication_events.authentication(content["token"], sid)
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", request.host, "authenticate", type(content), content, "OK")
    except Exception as e:
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%s]\n%s",
                       "SOCKET", request.host, "authenticate",
                       type(content), content, "ERROR", traceback_format_exc())
        emit('error', str(e), room=sid, namepace='/')


@socketio.on('disconnect')
def disconnection_event():
    authentication_events.disconnection(request.sid)
    logger.info("[%s] [%s] [%s] [%s]",
                "SOCKET", request.host, "disconnect", request.sid)
