from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify
from datetime import datetime
from dateutil import parser as dateparser

import time
import hashlib
import binascii
import os

from routes.utils import *

db_connect = create_engine('sqlite:///database.sqlt')

class AccountCreate(Resource):
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
        if check_subcription_json(content) == False:
            resp = jsonify({"success" : False, "error" : "missing element in json data"})
        elif check_subscription_duplicate(content) == False:
            resp = jsonify({"success" : False, "error" : "email already used"})
        else:
            hashed = hashlib.sha512(content['password'].encode('utf-8')).hexdigest()
            conn.execute("INSERT INTO user (email, password, fname, lname, birthday) VALUES (?, ?, ?, ?, ?)",
                        content['email'], hashed, content['fname'], content['lname'], dateparser.parse(content['birthday']))
            resp = jsonify({"success" : True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

class AccountLogin(Resource):
    def post(self):
        content = request.get_json()
        if verify_password(content['username'], content['password']) == False:
            resp = jsonify({"success" : False, "error" : "Wrong username or password"})
        else:
            token = hashlib.sha512(str(content['username'] + time.strftime("%c")).encode('utf-8')).hexdigest()
            conn = db_connect.connect()
            conn.execute("UPDATE user SET webtoken = ? WHERE email = ?", token, content['username'])
            resp = jsonify({"success" : True, "token" : token})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

class AccountLogout(Resource):
    def post(self):
        content = request.get_json()
        if verify_webtoken(content) == False:
            resp = jsonify({"success" : False, "error" : "Wrong token or username"})
        else:
            conn = db_connect.connect()
            conn.execute("UPDATE user SET webtoken = ? WHERE email = ?", '', content['username'])
            resp = jsonify({"success" : True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp        

class AccountInfo(Resource):
    def post(self):
        content = request.get_json()
        if verify_webtoken(content) == False:
            resp = jsonify({"success" : False, "error" : "Wrong token or username"})
        else:
            conn = db_connect.connect()
            query = conn.execute("SELECT * FROM user WHERE email = ?", content['username'])
            resp = {}
            for elem in query.cursor.fetchall():
                resp = jsonify({"id" : elem[0], "email" : elem[1], "fname" : elem[3], "lname" : elem[4], "birthday" : elem[5], "success" : True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

class AccountModify(Resource):
    def post(self):
        content = request.get_json()
        if verify_webtoken(content) == False:
            resp = jsonify({"success" : False, "error" : "Wrong token or username"})
        else:
            conn = db_connect.connect()
            query = conn.execute("SELECT * FROM user WHERE email = ?", content['username'])
            data = {}
            for elem in query.cursor.fetchall():
                data = {"email" : elem[1], "password" : elem[2], "fname" : elem[3], "lname" : elem[4], "birthday" : elem[5]}
            if 'email' in content:
                data['email'] = content['email']
            if 'lname' in content:
                data['lname'] = content['lname']
            if 'fname' in content:
                data['fname'] = content['fname']
            if 'password' in content:
                data['password'] = hashlib.sha512(content['password'].encode('utf-8')).hexdigest()
            if 'birthday' in content:
                data['birthday'] = dateparser.parse(content['birthday'])
            conn.execute("UPDATE user SET email = ?, password = ?, fname = ?, lname = ?, birthday = ? WHERE email = ?",
                        data['email'], data['password'], data['fname'], data['lname'], data['birthday'], content['username'])
            resp = jsonify({"success" : True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
