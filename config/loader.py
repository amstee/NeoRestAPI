import sys
import json
import os
import config.webrtc as webrtc
import config.hangout as hangout
import config.facebook as facebook
import config.database as database
import models.Device as Device
import models.User as User
import config.log as log


class ConfigLoader:
    config_file = "config.json"

    # Server variables
    port = 0
    host = ""
    debug = False

    # Project secret keys
    neo_secret = ""
    webrtc_secret = ""
    user_secret = ""
    device_secret = ""

    # Project database passwords
    admin_password = ""
    beta_user1_password = ""
    beta_user2_password = ""

    # Redis
    use_redis = False
    redis_url = ""

    # Project postgresql config
    postgresql_user = ""
    postgresql_password = ""
    postgresql_database = ""
    postgresql_host = ""
    postgresql_port = ""

    # Facebook API
    facebook_secret_token = ""
    facebook_page_access_token = ""

    # Hangout API
    hangout_token = ""
    hangout_config = {}

    # Logs
    log_activate = False
    log_level = ""

    def __init__(self, file=None):
        if file is not None:
            self.config_file = file

    def load_config(self):
        try:
            if not os.path.isfile(self.config_file):
                if os.path.isfile("../" + self.config_file):
                    self.config_file = "../" + self.config_file
                else:
                    raise FileNotFoundError
            with open(self.config_file) as f:
                data = json.load(f)
                if "project" in data:
                    self.port = data["project"]["port"]
                    self.host = data["project"]["host"]
                    self.debug = data["project"]["debug"]
                if "secrets" in data:
                    self.neo_secret = data["secrets"]["neo"]
                    self.webrtc_secret = data["secrets"]["webRTC"]
                    self.user_secret = data["secrets"]["userJWT"]
                    self.device_secret = data["secrets"]["deviceJWT"]
                if "redis" in data:
                    self.use_redis = data["redis"]["use"]
                    if self.use_redis:
                        self.redis_url = data["redis"]["url"]
                if "database" in data:
                    if "postgresql" in data["database"]:
                        self.postgresql_user = data["database"]["postgresql"]["user"]
                        self.postgresql_password = data["database"]["postgresql"]["password"]
                        self.postgresql_database = data["database"]["postgresql"]["database"]
                        self.postgresql_host = data["database"]["postgresql"]["host"]
                        self.postgresql_port = data["database"]["postgresql"]["port"]
                    self.admin_password = data["database"]["adminPassword"]
                    self.beta_user1_password = data["database"]["user1Password"]
                    self.beta_user2_password = data["database"]["user2Password"]
                if "facebook" in data:
                    self.facebook_secret_token = data["facebook"]["facebookSecretToken"]
                    self.facebook_page_access_token = data["facebook"]["facebookPageAccessToken"]
                if "hangout" in data:
                    self.hangout_secret = data["hangout"]["hangoutToken"]
                    self.hangout_config = data["hangout"]["hangoutConfig"]
                if "logs" in data:
                    self.log_activate = data["logs"]["activate"]
                    self.log_level = data["logs"]["level"]
        except FileNotFoundError as fnf:
            print("File error : %s" % fnf, file=sys.stderr)
            return False
        except KeyError as ke:
            print("Key error : %s" % ke, file=sys.stderr)
            return False
        return True

    def set_project_variables(self):
        webrtc.SECRET_KEY = self.webrtc_secret
        hangout.TOKEN = self.hangout_token
        hangout.KEY_FILE = self.hangout_config
        facebook.SECRET_TOKEN = self.facebook_secret_token
        facebook.PAGE_ACCESS_TOKEN = self.facebook_page_access_token
        database.POSTGRES["user"] = self.postgresql_user
        database.POSTGRES["pw"] = self.postgresql_password
        database.POSTGRES["db"] = self.postgresql_database
        database.POSTGRES["host"] = self.postgresql_host
        database.POSTGRES["port"] = self.postgresql_port
        Device.SECRET_KEY = self.device_secret
        User.SECRET_KEY = self.user_secret
        log.LOG_ACTIVATE = self.log_activate
        log.LOG_LEVEL = self.log_level


neo_config = ConfigLoader()
