class ContentException(Exception):
    message = str()
    status_code = int()
    pass


class JsonNotFound(ContentException):
    message = "Aucun JSON trouvé dans la requête"
    status_code = 405

    def __init__(self):
        ContentException.message = self.message
        ContentException.status_code = self.status_code


class JsonParameterNotFound(ContentException):
    def __init__(self, parameter):
        ContentException.message = "Champ JSON '%s' introuvable" % parameter
        ContentException.status_code = 400


class JsonParameterFormatError(ContentException):
    def __init__(self, parameter, type):
        ContentException.message = "Champ JSON '%s' n'est pas de type '%s'" % (parameter, type)
        ContentException.status_code = 400


class JsonUnreadable(ContentException):
    message = "JSON illisible ou malformé"
    status_code = 406

    def __init__(self):
        ContentException.message = self.message
        ContentException.status_code = self.status_code