from config import create_app, socketio, neoapi

if __name__ == '__main__':
    app = create_app()
    socketio.run(app=app, port=5000, host='0.0.0.0')
    # neo.app.run(port=5000, host='0.0.0.0')