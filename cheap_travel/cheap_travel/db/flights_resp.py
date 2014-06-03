from pymongo import MongoClient


class FlightsRespDAL(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client.flights_db
        self.flights_collection = db.flights_collection

    def save_data(self, key, data):
        data['key'] = key
        self.flights_collection.insert(data)

    def get_data(self, key):
        return self.flights_collection.find_one({"key": key})