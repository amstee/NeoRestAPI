from flask import Blueprint

sockets = Blueprint('sockets', __name__)

from . import standard_events
