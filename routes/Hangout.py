from flask import jsonify
from flask_restful import Resource
from utils.decorators import check_content
from bot.hangout import is_token_valid, link_user_to_hangout, is_user_linked, handle_conversation_payload
from bot.hangout import send_message_choice
from sys import stderr


class WebHookHangout(Resource):
    @check_content
    def post(self, content):
        try:
            if is_token_valid(content):
                if content['type'] == 'MESSAGE':
                    sender_id = content["space"]["name"]
                    message_text = content["message"]["text"]
                    split_message = message_text.split(' ')
                    if len(split_message) >= 2 and split_message[0] == "/token":
                        message = link_user_to_hangout(split_message[1], sender_id)
                        resp = jsonify({"text": message})
                    elif is_user_linked(sender_id):
                        resp = send_message_choice(sender_id, message_text)
                    else:
                        resp = jsonify({"text":"Votre compte hangout n'est lié a aucun compte NEO"})
                elif content['type'] == "CARD_CLICKED":
                    for elem in content['action']['parameters']:
                        resp = jsonify({"text" : handle_conversation_payload(elem['value'])})
                resp.status_code = 200
                return resp
            return
        except Exception as e:
            print(e, file=stderr)
            return
