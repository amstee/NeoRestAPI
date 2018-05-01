import json

def AuthenticateUser(api, user, password):
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