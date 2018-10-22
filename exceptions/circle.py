class CircleException(Exception):
    message = str()
    status_code = int()
    pass


class UserForbiddenAccess(CircleException):
    message = "Cet utilisateur n'a pas access a ce cercle"
    status_code = 403

    def __init__(self):
        CircleException.message = self.message
        CircleException.status_code = self.status_code


class CircleNotFound(CircleException):
    message = "Le cercle est introuvable"
    status_code = 404

    def __init__(self):
        CircleException.message = self.message
        CircleException.status_code = self.status_code


class InvitedUserNotFound(CircleException):
    message = "Utilisateur spécifié introuvable"
    status_code = 404

    def __init__(self):
        CircleException.message = self.message
        CircleException.status_code = self.status_code


class UserAlreadyPartOfCircle(CircleException):
    message = "L'utilisateur fait déjà partie de ce cercle"
    status_code = 400

    def __init__(self):
        CircleException.message = self.message
        CircleException.status_code = self.status_code


class UserNotPartOfCircle(CircleException):
    message = "Vous ne faite pas partie de ce cercle"
    status_code = 403

    def __init__(self):
        CircleException.message = self.message
        CircleException.status_code = self.status_code


class TargetUserNotPartOfCircle(CircleException):
    message = "L'utilisateur ne fait pas partie de ce cercle"
    status_code = 403

    def __init__(self):
        CircleException.message = self.message
        CircleException.status_code = self.status_code


class InvitationNotFound(CircleException):
    message = "Invitation introuvable"
    status_code = 404

    def __init__(self):
        CircleException.message = self.message
        CircleException.status_code = self.status_code


class UnallowedToUseInvitation(CircleException):
    message = "Vous n'êtes pas autorisé à utilisé cette invitation"
    status_code = 403

    def __init__(self):
        CircleException.message = self.message
        CircleException.status_code = self.status_code


