import json

with open('config.json') as data_file:
    neo_config = json.load(data_file)

EXPIRY = 86400
SECRET_KEY = neo_config["secrets"]["webRTC"]

TURN = [
    {
        "domain": "webrtc.neo.ovh",
        "ip": "",
        "port": 3478
    }
]

STUN = [
    {
        "domain": "webrtc.neo.ovh",
        "ip": "",
        "port": 3478,
    }
]
