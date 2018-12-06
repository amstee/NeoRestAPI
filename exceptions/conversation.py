class ConversationException(Exception):
    message = str()
    status_code = int()
    pass


class UserForbiddenAccess(ConversationException):
    message = "Cet utilisateur n'a pas accès à cette conversation"
    status_code = 403

    def __init__(self):
        ConversationException.message = self.message
        ConversationException.status_code = self.status_code


class TargetUserNotPartOfConversation(ConversationException):
    message = "L'utilisateur cible ne fait pas partie de cette conversation"
    status_code = 403

    def __init__(self):
        ConversationException.message = self.message
        ConversationException.status_code = self.status_code


class InsufficientRight(ConversationException):
    message = "Cet utilisateur n'a pas les droits suffisants pour modifier cette conversation"
    status_code = 403

    def __init__(self):
        ConversationException.message = self.message
        ConversationException.status_code = self.status_code


class ConversationNotFound(ConversationException):
    message = "Conversation introuvable"
    status_code = 404

    def __init__(self):
        ConversationException.message = self.message
        ConversationException.status_code = self.status_code


class SpecifiedUserNotFound(ConversationException):
    message = "Utilisateur spécifié introuvable"
    status_code = 404

    def __init__(self):
        ConversationException.message = self.message
        ConversationException.status_code = self.status_code


class UserAlreadyPartOfConversation(ConversationException):
    message = "L'utilisateur fait déjà parti de la conversation"
    status_code = 409

    def __init__(self):
        ConversationException.message = self.message
        ConversationException.status_code = self.status_code