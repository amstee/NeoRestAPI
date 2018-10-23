class MediaException(Exception):
    message = str()
    status_code = int()
    pass


class MediaNotFound(MediaException):
    message = "Media introuvable"
    status_code = 404

    def __init__(self):
        MediaException.message = self.message
        MediaException.status_code = self.status_code


class ForbiddenAccess(MediaException):
    message = "Vous n'avez pas accès à ce media"
    status_code = 403

    def __init__(self):
        MediaException.message = self.message
        MediaException.status_code = self.status_code


class ForbiddenUpload(MediaException):
    message = "Vous ne pouvez pas upload ce media"
    status_code = 403

    def __init__(self):
        MediaException.message = self.message
        MediaException.status_code = self.status_code


class MediaNotFoundInSystem(MediaException):
    message = "Le media est introuvable dans le système"
    status_code = 404

    def __init__(self):
        MediaException.message = self.message
        MediaException.status_code = self.status_code


class MediaNotFoundInRequest(MediaException):
    message = "Le media est introuvable dans la requête"
    status_code = 404

    def __init__(self):
        MediaException.message = self.message
        MediaException.status_code = self.status_code


class PurposeNotFound(MediaException):
    message = "'purpose' introuvable"
    status_code = 404

    def __init__(self):
        MediaException.message = self.message
        MediaException.status_code = self.status_code
