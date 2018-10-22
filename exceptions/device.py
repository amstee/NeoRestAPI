class DeviceException(Exception):
    message = str()
    status_code = int()
    pass


class DeviceForbiddenAccess(DeviceException):
    message = "Vous n'avez pas accès a cette machine NEO"
    status_code = 403

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class InvalidActivationKey(DeviceException):
    message = "Clée d'activation invalide"
    status_code = 400

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class NoDeviceForUser(DeviceException):
    message = "Aucune machine NEO n'appartient cet utilisateur"
    status_code = 400

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class MismatchOldPassword(DeviceException):
    message = "L'ancien mot de passe ne correspond pas"
    status_code = 400

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class NotPartOfDeviceCircle(DeviceException):
    message = "Vous ne faite pas partie du cercle de cette machine NEO"
    status_code = 403

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class DeviceNameAlreadyExist(DeviceException):
    message = "Le nom de device existe déja"
    status_code = 400

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class DeviceNotFound(DeviceException):
    message = "Machine NEO introuvable"
    status_code = 404

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class UnactivatedDevice(DeviceException):
    message = "Machine NEO non activé"
    status_code = 412

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class UnauthenticatedDevice(DeviceException):
    message = "Machine NEO non authentifié"
    status_code = 401

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code


class TokenNotBoundToDevice(DeviceException):
    message = "Le token d'authentification ne correspond à aucune machine NEO"
    status_code = 404

    def __init__(self):
        DeviceException.message = self.message
        DeviceException.status_code = self.status_code
