from flask import Blueprint

sockets = Blueprint('sockets', __name__)

from . import standard_events
from . import room_events
from . import message_events
