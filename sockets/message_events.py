from models.UserToConversation import UserToConversation
from config.database import db_session
from config import socketio, sockets
from flask import request
from flask_socketio import join_room, leave_room, emit, send
from utils.contentChecker import contentChecker
from models.Conversation import Conversation
from models.Media import Media
from models.Message import Message
from routes.Facebook import *
import datetime

@socketio.on('message')
def message(content):
    sid = request.sid
    socket = sockets.find_socket(sid)
    if socket is None:
        emit('error', 'Socket user introuvable', room=sid)
    else:
        try:
            #contentChecker("files", "link_id", "text", "directory_name")
            file_list = content["files"]
            link = db_session.query(UserToConversation).filter(UserToConversation.id==content["link_id"]).first()
            if link is None:
                socket.emit('error', "Lien entre utilisateur et conversation introuvable")
            else:
                message = Message(content=content["text"])
                message.link = link
                message.conversation = link.conversation
                for file in file_list:
                    if file in request.files:
                        new_file = Media().setContent(request.files[file], content["directory_name"], message)
                        message.medias.append(new_file)
                db_session.commit()
                conversation = db_session.query(Conversation).filter(link.conversation_id == Conversation.id).first()
                info_sender = "[" + link.conversation.name + "] " + socket.user.first_name + " : " 
                MessengerConversationModelSend(link.user_id, conversation, info_sender + message.text_content)
                data_socket = {
                    'id': socket.user.id,
                    'conversation_id': conversation.id,
                    'username': socket.user.first_name,
                    'message': message.text_content,
                    'time': datetime.datetime.now()
                }
                socket.emit('message', data_socket, room=conversation.id)
                socket.emit("success", "Message sent")
        except Exception as e:
            socket.emit("error", str(e))