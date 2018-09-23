from flask_restful import Resource
from utils.decorators import secured_route, check_content_old, secured_user_route
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.exceptions import ContentNotFound
import core.conversation_logic as core


class ConversationInvite(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("conversation_id", "email")
            return core.invite(content["conversation_id"], content["email"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class ConversationUserPromote(Resource):
    @check_content_old
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("conversation_id", "email")
            return core.user_promote(content["conversation_id"], content["email"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class ConversationKick(Resource):
    @check_content_old
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("conversation_id", "email")
            return core.conversation_kick(content["conversation_id"], content["email"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class ConversationQuit(Resource):
    @check_content_old
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            return core.conversation_quit(content["conversation_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class ConvesationSetDevice(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("conversation_id")
            return core.set_device(content["conversation_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)
