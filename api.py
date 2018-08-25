from gevent import monkey
monkey.patch_all()

import sys
from config.loader import neo_config
from config import create_app, socketio, NeoAPI, sockets


if __name__ == '__main__':
    if neo_config.load_config():
        neo_config.set_project_variables()
        app = create_app(neo_config)
        socketio.run(app=app, port=neo_config.port, host=neo_config.host, debug=neo_config.debug)
        sys.exit(0)
    else:
        print("An error occured loading the configuration file", file=sys.stderr)
        sys.exit(1)
