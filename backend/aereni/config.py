class Config:
    def __init__(self):
        self.org = None
        self.bucket = None

    def set_config(self, config):
        self.org = config["INFLUXDB_V2_ORG"]
        self.bucket = config["INFLUXDB_V2_BUCKET"]

config = Config()
