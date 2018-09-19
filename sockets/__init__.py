from flask import Blueprint

sockets = Blueprint('sockets', __name__)

from . import authentication
from . import rooms
from . import message
from . import webrtc
