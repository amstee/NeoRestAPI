class MessageException(Exception):
    message = str()
    status_code = int()
    pass


class MessageNotFound(MessageException):
    message = "Message introuvable"
    status_code = 404

    def __init__(self):
        MessageException.message = self.message
        MessageException.status_code = self.status_code


class TargetUserNotFound(MessageException):
    message = "Destinataire introuvable"
    status_code = 404

    def __init__(self):
        MessageException.message = self.message
        MessageException.status_code = self.status_code


class ForbiddenAccess(MessageException):
    message = "Vous n'avez pas accès à ce message"
    status_code = 403

    def __init__(self):
        MessageException.message = self.message
        MessageException.status_code = self.status_code


class MessageQuantityInvalid(MessageException):
    message = "Quantité de message invalide"
    status_code = 400

    def __init__(self):
        MessageException.message = self.message
        MessageException.status_code = self.status_code
