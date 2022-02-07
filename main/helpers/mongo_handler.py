import logging
import datetime


class MongoHandler(logging.Handler):

    def __init__(self, mongo_db, level=logging.NOTSET, collection='log', capped=True, size=100000,
                 drop=False):
        logging.Handler.__init__(self, level)
        self.database = mongo_db

        if collection in self.database.collection_names():
            if drop:
                self.database.drop_collection(collection)
                self.collection = self.database.create_collection(name=collection, capped=capped, size=size)
            else:
                self.collection = self.database[collection]
        else:
            self.collection = self.database.create_collection(name=collection, capped=capped, size=size)

    def emit(self, record):
        self.collection.save({'when': datetime.datetime.now(),
                              'levelno': record.levelno,
                              'levelname': record.levelname,
                              'message': record.msg})