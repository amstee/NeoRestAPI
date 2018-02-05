from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify
from datetime import datetime
from dateutil import parser as dateparser
from flask_httpauth import HTTPBasicAuth

import hashlib
import binascii
import os


db_connect = create_engine('sqlite:///database.sqlt')
auth = HTTPBasicAuth()


class Account(Resource):
    def get(sefl):
        conn = db_connect.connect()
        query = conn.execute("select * from user")
        result = []
        for elem in query.cursor.fetchall():
            result.append({"id" : elem[0], "email" : elem[1], "fname" : elem[3], "lname" : elem[4], "birthday" : elem[5]})
        resp = jsonify(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def post(self):
        content = request.get_json()
        conn = db_connect.connect()
        hashed = hashlib.sha512(content['password']).hexdigest()
        conn.execute("INSERT INTO user (email, password, fname, lname, birthday) VALUES (?, ?, ?, ?, ?)",
                    content['email'], hashed, content['fname'], content['lname'], dateparser.parse(content['birthday']))
        resp = jsonify({"success" : True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

class User(Resource):
    @auth.verify_password
    def verify_password(username, password):
        conn = db_connect.connect()
        query = conn.execute("SELECT * FROM user WHERE email=?", username)
        SHA512password = ''
        tmp = []
        for mpass in query.cursor.fetchall():
            tmp.append({"id" : mpass[0], "email" : mpass[1], "fname" : mpass[3], "lname" : mpass[4], "birthday" : mpass[5]})
            SHA512password = mpass[2]
        if SHA512password != hashlib.sha512(password).hexdigest():
            tmp = jsonify({"success" : False})
            return False
        getAuthData = tmp
        return True

    @auth.login_required
    def get(self, user):
        resp = jsonify({"success" : True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

class UserModify(Resource):
    def post(self, user):
        content = request.get_json()
        conn = db_connect.connect()
        conn.execute("UPDATE user SET fname = ?, lname = ?, birthday = ? WHERE email = ?",
                    content['fname'], content['lname'], dateparser.parse(content['birthday']), content['email'])
        resp = jsonify({"success" : True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
