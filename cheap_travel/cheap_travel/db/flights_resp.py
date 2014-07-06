from pymongo import MongoClient
import csv
import constants


class FlightsRespDAL(object):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client.flights_db

        self.flights_collection = db.flights_collection
        self.flights_collection.create_index("key")

        self.airport_collection = db.airport_collection
        self.airport_collection.create_index("airport_code")

        self.airline_collection = db.airline_collection
        self.airline_collection.create_index("airline_code")

        self.results_collection = db.results_collection


        self.insert_airlines_to_db()
        self.insert_airports_to_db()

        #remove all keys without values
        self.flights_collection.remove({"value": None})


    def insert_airlines_to_db(self):
        if self.get_airline("DL") is not None:
            return

        with open('airlines.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                try:
                    if row[0] != "" and row[1] != "":
                        new_dict = {}
                        new_dict['airline_code'] = row[1]
                        new_dict['airline_name'] = row[0]
                        self.airline_collection.insert(new_dict)

                except:
                    continue

    def insert_airports_to_db(self):
        if self.get_airport("AMS") is not None:
            return

        with open('airport-codes.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in reader:
                try:
                    if row[0] != "" and row[1] != "" and row[2] != "":
                        new_dict = {}
                        new_dict['airport_code'] = row[2].strip('",')
                        new_dict['airport_country'] = row[1].strip('",')
                        new_dict['airport_name'] = row[0].strip('",')
                        self.airport_collection.insert(new_dict)

                except:
                    continue

    def insert_results_to_db(self, key, data):
        self.results_collection.update({"key": key}, {"$push": {"connections": data}}, upsert=True)

    def set(self, key, data):
        self.remove(key)

        new_dict = {}
        new_dict['key'] = key
        new_dict['value'] = data
        self.flights_collection.insert(new_dict)


    def get(self, key):
        data = self.flights_collection.find_one({"key": key}, fields= { 'value.Journeys' : { "$slice": constants.MAX_FLIGHTS_PER_TRIP }})
        if data:
            return data['value']
        else:
            return

    def has_key(self, key):
        return self.flights_collection.find_one({"key": key}, fields= { 'value.Journeys' : { "$slice": 1 }}) is not None

    def remove(self, key):
        self.flights_collection.remove({"key": key})

    def get_airport(self, code):
        value = self.airport_collection.find_one({"airport_code": code})
        if value:
            return value['airport_name']
        return None

    def get_airline(self, code):
        value = self.airline_collection.find_one({"airline_code": code})
        if value:
            return value['airline_name']
        return None
