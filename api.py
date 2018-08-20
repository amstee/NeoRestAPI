from gevent import monkey
monkey.patch_all()

from config import create_app, socketio, NeoAPI

if __name__ == '__main__':
    app = create_app()
    socketio.run(app=app, port=5000, host='0.0.0.0', debug=True)
