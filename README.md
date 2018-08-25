# NeoRestAPI
Neo Restfull API &amp; Websocket server

## Installation

Write the following commands
* git clone git@github.com:amstee/NeoRestAPI.git && cd NeoRestAPI
* virtualenv -p "PATH TO YOUR PYTHON3" venv
* source venv/bin/activate
* pip install -r requirements.txt<br/>

And you're all set !

## Configuration

To start the server, you'll need to create the configuration file (default: config.json)

A default configuration would be :<br/>
```json
{
  "project": {
    "port": 5000,
    "host": "0.0.0.0",
    "debug": false
  },
  "secrets": {
    "neo": "",
    "webRTC": "",
    "userJWT": "",
    "deviceJWT": ""
  },
  "database": {
    "postgresql": {
      "user": "",
      "password": "",
      "database": "",
      "host": "",
      "port": ""
    },
    "adminPassword": "",
    "user1Password": "",
    "user2Password": ""
  },
  "redis": {
    "url": ""
  },
  "facebook": {    
  },
  "hangout": {
  }
}
```

## Start the server

Once the configuration file has been created you can start the server :<br/>
**python api.py**

## Docker

A Docker implementation would be
```dockerfile
FROM python:3.6

COPY . /NeoRestAPI
WORKDIR /NeoRestAPI
RUN pip3 install -r requirements.txt

EXPOSE 5000
CMD ["python3", "api.py"]
```