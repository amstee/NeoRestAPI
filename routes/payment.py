from flask_restful import Resource
from utils.contentChecker import content_checker
from utils.decorators import secured_user_route, check_content
from utils.apiUtils import *
from utils.exceptions import ContentNotFound
import core.payment as core


class FakePayment(Resource):
    @check_content
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            return core.fake_pay(content, content["circle_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)