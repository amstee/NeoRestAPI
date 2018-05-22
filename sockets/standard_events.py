from config import socketio

@socketio.on("connect")
def connected():
    print("client connection")

@socketio.on('client_connected')
def handle_client_connect_event(json):
    print('received json: {0}'.format(str(json)))
