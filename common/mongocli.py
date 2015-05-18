# encoding=utf-8
import pymongo
from common import log

class PyMongoHandler(object):
    """mongoDB客户端连接基础类, 同步调用版本"""
    def __init__(self, db_host, db_port, db_name, db_user, db_passwd):
        self._table = None
        self._dbclient = pymongo.MongoClient(db_host, db_port)
        self._database = self._dbclient[db_name]
        ret = self._database.authenticate(db_user, db_passwd)
        if not ret:
            log.ERROR('<sync> connect to database[%s]... fail' % db_name)
        else:
            log.INFO('<sync> connect to database[%s]... done' % db_name)

    def __del__(self):
        if self._database:
            self._database.logout()

    def connect_table(self, table_name):
        self._table = self._database[table_name]
        if self._table is not None:
            log.INFO('<sync> connect collection[%s] ... done' % table_name)

    def alive(self):
        if self._dbclient:
            state = self._dbclient.alive()
            if state == False:
                log.ERROR('<sync> mongoDB disconnected')
            return state
        else:
            log.ERROR('<sync> mongoDB disconnected')
            return False

    def table_insert(self, dictdata):
        if self.alive():
            self._table.insert(dictdata)

    def table_find_one(self, condition1, condition2=None):
        if self.alive():
            result = self._table.find_one(condition1, condition2)
            return result

    def get_max_players(self):
        if self.alive():
            max_players = []
            results = self._table.find({'contact':{'$exists': True}, 'price': {'$ne': 0}}).sort([('price', -1), ('update_time', 1)]).limit(3)
            for result in results:
                max_players.append(result)

            return max_players

    def get_max_price(self):
        if self.alive():
            results = self._table.find({'contact':{'$exists': True}, 'price': {'$ne': 0}}).sort({'price': -1, 'update_time': 1}).limit(1)
            for result in results:
                return result['price']

    def table_update(self, field1, field2):
        if isinstance(field1, dict) and isinstance(field2, dict) and self.alive():
            self._table.update(field1, {'$set': field2}, multi=True)
            return True
        else:
            return False

    def table_update_unset(self, field1, field2):
        if isinstance(field1, dict) and isinstance(field2, dict) and self.alive():
            self._table.update(field1, {'$unset': field2}, multi=True)
            return True
        else:
            return False
