#encoding=utf-8
from common import config


class RobotConfig(config.ConfigHandler):
    def __init__(self):
        super(RobotConfig, self).__init__('config.cfg', 'info')

        self.token = self.fread('access_token')
        self.mongo_host = self.fread('mongo_host')
        self.mongo_port = int(self.fread('mongo_port'))
        self.mongo_user = self.fread('mongo_user')
        self.mongo_passwd = self.fread('mongo_passwd')
        self.mongo_db = self.fread('mongo_db')
        self.mongo_member = self.fread('mongo_member_table')
        self.mongo_auction = self.fread('mongo_auction_table')
