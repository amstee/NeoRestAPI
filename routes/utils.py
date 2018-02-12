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

db_connect = create_engine('sqlite:///database.sqlt')

def verify_webtoken(content):
    if 'username' not in content or 'token' not in content:
        return False
    if content['token'] == '':
        return False
    conn = db_connect.connect()
    query = conn.execute("SELECT * FROM user WHERE email=?", content['username'])
    for elem in query.cursor.fetchall():
        if elem[6] == content['token']:
            return True
    return False

def verify_password(username, password):
    conn = db_connect.connect()
    query = conn.execute("SELECT * FROM user WHERE email=?", username)
    SHA512password = ''
    tmp = []
    for mpass in query.cursor.fetchall():
        tmp.append({"id" : mpass[0], "email" : mpass[1], "fname" : mpass[3], "lname" : mpass[4], "birthday" : mpass[5]})
        SHA512password = mpass[2]
    if SHA512password != hashlib.sha512(password.encode('utf-8')).hexdigest():
        return False
    return True

def check_subcription_json(content):
    if 'email' not in content or 'fname' not in content or 'lname' not in content or 'birthday' not in content or 'password' not in content:
        return False
    return True

def check_subscription_duplicate(content):
    conn = db_connect.connect()
    query = conn.execute("SELECT * FROM user WHERE email=?", content['email'])
    for elem in query.cursor.fetchall():
        if elem[1] == content['email']:
            return False
    return True
