from flask_sqlalchemy import SQLAlchemy

POSTGRES = {
    'user': '',
    'pw': '',
    'db': '',
    'host': '',
    'port': '',
}
URI_POSTGRES = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
URI_SQLITE = 'sqlite:///database.sqlt'
URI_TESTING = 'sqlite:///:memory:'

URI_USED = URI_SQLITE

db = SQLAlchemy()


def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
