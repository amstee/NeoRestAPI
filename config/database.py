from flask_sqlalchemy import SQLAlchemy
import json

with open('config.json') as data_file:
    neo_config = json.load(data_file)

POSTGRES = {
    'user': neo_config["database"]["postgresql"]["user"],
    'pw': neo_config["database"]["postgresql"]["password"],
    'db': neo_config["database"]["postgresql"]["database"],
    'host': neo_config["database"]["postgresql"]["host"],
    'port': neo_config["database"]["postgresql"]["port"]
}

TYPE = {
    "POSTGRESQL": 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES,
    "SQLITE": 'sqlite:///database.sqlt',
    "TESTING": 'sqlite:///:memory:'
}

URI_USED = TYPE[neo_config["database"]["type"]]

db = SQLAlchemy()


def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
