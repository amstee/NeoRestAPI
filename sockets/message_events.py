from models.UserToConversation import UserToConversation
from config.database import db_session
from config import socketio, sockets
from flask import request
from flask_socketio import emit
from utils.contentChecker import check_json
from models.Conversation import Conversation
from models.Media import Media
from models.Message import Message
from routes.Facebook import MessengerConversationModelSend
from bot.hangout import hangout_conversation_model_send


@socketio.on('writing')
def is_writing(json):
    sid = request.sid
    socket = sockets.find_socket(sid)
    if socket is None or socket.authenticated is False:
        emit('error', 'Socket user introuvable', room=sid, namespace='/')
    else:
        try:
            b, s = check_json('conversation_id', 'is_writing')
            if not b:
                socket.emit('error', 'Parameter missing')
            else:
                if socket.is_device:
                    emit('writing', {'conversation_id': json['conversation_id'], 'device': True,
                                     'is_writing': json['is_writing']},
                         room='conversation_' + str(json['conversation_id']), namespace='/')
                else:
                    emit('writing', {'conversation_id': json['conversation_id'], 'device': False,
                                     'user': socket.client.email, 'is_writing': json['is_writing']},
                         room='conversation_'+str(json['conversation_id']), namespace='/')
        except Exception as e:
            socket.emit('error', str(e))


@socketio.on('message')
def message_send(content):
    sid = request.sid
    socket = sockets.find_socket(sid)
    if socket is None or socket.authenticated is False:
        emit('error', 'Socket user introuvable', room=sid, namespace='/')
    else:
        try:
            b, s = check_json(content, 'conversation_id')
            if not b:
                emit('error', 'Param conversation_id introuvable', room=sid, namespace='/')
            else:
                conv = db_session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
                if conv is None:
                    emit('error', 'Conversation introuvable', room=sid, namespace='/')
                else:
                    if socket.is_device:
                        message = Message(content=content["text_message"] if "text_message" in content else "",
                                          is_user=False)
                        message.conversation = conv
                        message.device = socket.client
                    else:
                        link = db_session.query(UserToConversation).\
                            filter(UserToConversation.user_id == socket.client.id,
                                   UserToConversation.conversation_id == conv.id).first()
                        if link is None:
                            emit('error', "Vous ne faites pas partie de cette conversation", room=sid, namespace='/')
                            return
                        else:
                            message = Message(content=content['text_message'] if 'text_message' in content else '')
                            message.conversation = conv
                            message.link = link
                    db_session.commit()
                    try:
                        MessengerConversationModelSend(socket.client.id, conv, content["text_message"])
                    except Exception:
                        pass
                    try:
                        hangout_conversation_model_send(socket.client.id, conv, content["text_message"])
                    except Exception:
                        pass
                    media_list = []
                    if 'files' in content:
                        for file in content["files"]:
                            media = Media()
                            media.identifier = file
                            media.message = message
                            db_session.commit()
                            media_list.append(media.get_simple_content())
                        socket.emit('media', {'media_list': media_list, 'message_id': message.id})
                    socket.emit('success', {'received': True, 'message_id': message.id})
                    if not media_list:
                        emit('message', {
                            'conversation_id': conv.id,
                            'message': message.get_simple_json_compliant_content(),
                            'time': message.sent.isoformat(),
                            'sender': socket.client.get_simple_json_compliant_content(),
                            'media_list': media_list,
                            'status': 'done'},
                             room='conversation_' + str(conv.id), namespace='/')
                    else:
                        emit('message', {'conversation_id': conv.id,
                                         'message': message.get_simple_json_compliant_content(),
                                         'status': 'pending'}, room='conversation_' + str(conv.id), namespace='/')
        except Exception as e:
            socket.emit("error", str(e), namespace='/')
