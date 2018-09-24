from flask_restful import Resource
from utils.decorators import secured_route_old, check_content_old, secured_user_route
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.exceptions import ContentNotFound
import core.circle_logic as core


class CircleInvite(Resource):
    @check_content_old
    @secured_route_old
    def post(self, content, client, is_device):
        try:
            content_checker("circle_id", "email")
            return core.invite(content["circle_id"], content["email"],  client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CircleJoin(Resource):
    @check_content_old
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("invite_id")
            return core.join(content["invite_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CircleReject(Resource):
    @check_content_old
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("invite_id")
            return core.refuse_invite(content["invite_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CircleQuit(Resource):
    @check_content_old
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            return core.quit_circle(content["circle_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CircleKick(Resource):
    @check_content_old
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("email", "circle_id")
            return core.kick_user(content["email"], content["circle_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)
