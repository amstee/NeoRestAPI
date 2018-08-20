import json


def authenticate_user(api, user, password):
    if type(user) is str:
        varia = user
    else:
        varia = user.email
    json_data = {
        "email": varia,
        "password": password
    }
    response = api.post('/account/login', data=json.dumps(json_data), content_type='application/json')
    response_json = json.loads(response.data)
    return response_json['token']


def authenticate_device(api, device, password):
    if type(device) is str:
        varia = device
    else:
        varia = device.username
    json_data = {
        "device_username": varia,
        "device_password": password
    }
    response = api.post('/device/authenticate', data=json.dumps(json_data), content_type='application/json')
    response_json = json.loads(response.data)
    return response_json['device_token']
