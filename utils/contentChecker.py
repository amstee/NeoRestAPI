from flask import request
from flask.ext.jsonpify import jsonify
from models.User import User

def contentChecker(*args):
    content = request.get_json()
    for string in args:
        if string not in content:
            raise Exception("Parametre %s introuvable dans le contenu de la requete"%string)
        # if type(content[string]) != type:
        #     raise Exception("Le type du parametre %s est invalide %s expected"%(string, str(type)))