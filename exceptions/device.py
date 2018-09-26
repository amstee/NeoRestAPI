class DeviceException(Exception):
    message = str()
    status_code = int()
    pass


class DeviceNotFound(DeviceException):
    def __init__(self):
        DeviceException.message = "Machine NEO introuvable"
        DeviceException.status_code = 404


class UnactivatedDevice(DeviceException):
    def __init__(self):
        DeviceException.message = "Machine NEO non activé"
        DeviceException.status_code = 412


class UnauthenticatedDevice(DeviceException):
    def __init__(self):
        DeviceException.message = "Machine NEO non authentifié"
        DeviceException.status_code = 401


class TokenNotBoundToDevice(DeviceException):
    def __init__(self):
        DeviceException.message = "Le token d'authentification ne correspond à aucune machine NEO"
        DeviceException.status_code = 404
