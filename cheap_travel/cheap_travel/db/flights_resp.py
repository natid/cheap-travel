from pymongo import MongoClient


class FlightsRespDAL(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client.flights_db
        self.flights_collection = db.flights_collection
        self.flights_collection.create_index("key")

    def set(self, key, data):
        self.remove(key)

        new_dict = {}
        new_dict['key'] = key
        new_dict['value'] = data
        self.flights_collection.insert(new_dict)

    def get(self, key):
        data = self.flights_collection.find_one({"key": key})
        if data:
            return data['value']
        else:
            return

    def has_key(self, key):
        return self.flights_collection.find_one({"key": key}) is not None

    def remove(self, key):
        self.flights_collection.remove({"key": key})
