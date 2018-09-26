class AccountException(Exception):
    message = str()
    status_code = int()
    pass


class EmailAlreadyUsed(AccountException):
    def __init__(self):
        AccountException.message = "Cette adresse email est déja utilisé"
        AccountException.status_code = 409


class UserNotFound(AccountException):
    def __init__(self):
        AccountException.message = "Utilisateur introuvable"
        AccountException.status_code = 404


class TokenNotBoundToUser(AccountException):
    def __init__(self):
        AccountException.message = "Le token d'authentification ne correspond à aucun utilisateur"
        AccountException.status_code = 404


class MismatchingPassword(AccountException):
    def __init__(self):
        AccountException.message = "Le mot de passe de correspond pas"
        AccountException.status_code = 417


class InvalidPassword(AccountException):
    def __init__(self):
        AccountException.message = "Le mot de passe est invalide"
        AccountException.status_code = 401


class UnauthenticatedUser(AccountException):
    def __init__(self):
        AccountException.message = "Utilisateur non authentifié"
        AccountException.status_code = 401


class ExpiredUserSession(AccountException):
    def __init__(self):
        AccountException.message = "La session a expiré, authentifiez vous a nouveau"
        AccountException.status_code = 401


class InvalidJwtToken(AccountException):
    def __init__(self):
        AccountException.message = "Token invalide, authentifiez vous a nouveau"
        AccountException.status_code = 401


class NotAllowedToSeeUser(AccountException):
    def __init__(self):
        AccountException.message = "Vous ne pouvez pas voir cet utilisateur"
        AccountException.status_code = 403


class InsufficientAccountRight(AccountException):
    def __init__(self):
        AccountException.message = "Les droits de votre compte sont insuffisant"
        AccountException.status_code = 403

