from flask import request


def contentChecker(*args):
    content = request.get_json()
    for string in args:
        if string not in content:
            raise Exception("Parametre %s introuvable dans le contenu de la requete"%string)


def check_json(content, *args):
    for string in args:
        if string not in content:
            return False, string
    return True, None