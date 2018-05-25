from flask import Blueprint

sockets = Blueprint('sockets', __name__)

from . import standard_events
# from . import ChannelHandler
#
# AccountHandler = ChannelHandler.ChannelHandler('/account')
# CircleHandler = ChannelHandler.ChannelHandler('/circle')
# DeviceHandler = ChannelHandler.ChannelHandler('/device')
# ConversationHandler = ChannelHandler.ChannelHandler('/conversation')