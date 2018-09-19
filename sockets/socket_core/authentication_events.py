from config import sockets
from utils.log import logger_set
from config.log import LOG_SOCKET_FILE

logger = logger_set(module=__name__, file=LOG_SOCKET_FILE)


def authentication(token, sid):
    socket = sockets.new_client(sid)
    b, data = socket.authenticate(token)
    sockets.save_client(socket)
    if not b:
        raise Exception(data)
    socket.emit('success', data)
    return True


def disconnection(sid):
    sockets.remove(sid)
    return True
