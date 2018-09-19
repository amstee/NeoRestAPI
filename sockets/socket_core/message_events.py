from models.UserToConversation import UserToConversation
from config.database import db
from flask_socketio import emit
from models.Conversation import Conversation
from models.Media import Media
from models.Message import Message
from bot.facebook import messenger_conversation_model_send
from bot.hangout import hangout_conversation_model_send
from utils.log import logger_set
from config.log import LOG_SOCKET_FILE

logger = logger_set(module=__name__, file=LOG_SOCKET_FILE)


def is_writing(conversation_id, is_w, socket):
    client = socket.get_client()
    if socket.is_device:
        emit('writing', {'conversation_id': conversation_id, 'device': True,
                         'is_writing': str(is_w)},
             room='conversation_' + str(conversation_id), namespace='/')
    else:
        emit('writing', {'conversation_id': conversation_id, 'device': False,
                         'user': client.email, 'is_writing': str(is_w)},
             room='conversation_' + str(conversation_id), namespace='/')


def message_send(conversation_id, content, socket):
    client = socket.get_client()
    conv = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conv is None:
        raise Exception('Conversation introuvable')
    if socket.is_device:
        message = Message(content=content["text_message"] if "text_message" in content else "",
                          is_user=False)
        message.conversation = conv
        message.device = client
    else:
        link = db.session.query(UserToConversation). \
            filter(UserToConversation.user_id == socket.client_id,
                   UserToConversation.conversation_id == conv.id).first()
        if link is None:
            raise Exception("Vous ne faites pas partie de cette conversation")
        message = Message(content=content['text_message'] if 'text_message' in content else '')
        message.conversation = conv
        message.link = link
    db.session.commit()
    try:
        messenger_conversation_model_send(socket.client_id, conv, content["text_message"])
    except Exception as e:
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", "", "message", type(content), content, "FACEBOOK FAILED : " + str(e))
    try:
        hangout_conversation_model_send(socket.client_id, conv, content["text_message"])
    except Exception as e:
        logger.info("[%s] [%s] [%s] [%s] [%s] [%s]",
                    "SOCKET", "", "message", type(content), content, "HANGOUT FAILED : " + str(e))
    media_list = []
    if 'files' in content:
        for file in content["files"]:
            media = Media()
            media.identifier = file
            media.message = message
            db.session.commit()
            media_list.append(media.get_simple_content())
        socket.emit('media', {'media_list': media_list, 'message_id': message.id})
    socket.emit('success', {'received': True, 'message_id': message.id})
    if not media_list:
        emit('message', {
            'conversation_id': conv.id,
            'message': message.get_simple_json_compliant_content(),
            'time': message.sent.isoformat(),
            'sender': client.get_simple_json_compliant_content(),
            'media_list': media_list,
            'status': 'done'},
             room='conversation_' + str(conv.id), namespace='/')
    else:
        emit('message', {'conversation_id': conv.id,
                         'message': message.get_simple_json_compliant_content(),
                         'status': 'pending'}, room='conversation_' + str(conv.id), namespace='/')
