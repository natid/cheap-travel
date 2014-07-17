from pymongo import MongoClient
import csv
import constants
import os

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

        self.connections_collection = db.connections_collection
        self.connections_collection.create_index("area")

        self.insert_airlines_to_db()
        self.insert_airports_to_db()

        #remove all keys without values
        self.flights_collection.remove({"value": None})


    def insert_airlines_to_db(self):
        if self.get_airline("DL") is not None:
            return

        with open('db/airlines.csv', 'rb') as csvfile:
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

        with open('db/airport-codes.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in reader:
                try:
                    if row[0] != "" and row[1] != "" and row[2] != "" and len(row[2].strip('",')) < 5 and  len(row[2].strip('",')) > 1:
                        new_dict = {}
                        new_dict['airport_code'] = row[2].strip('",')
                        new_dict['airport_country'] = row[1].strip('",')
                        new_dict['airport_name'] = row[0].strip('",')
                        self.airport_collection.insert(new_dict)

                except:
                    continue

    def insert_results_to_db(self, key, data):
        self.results_collection.update({"key": key}, {"$push": {"connections": data}}, upsert=True)

    def get_results(self, key):
        data = self.results_collection.find_one({"key": key})
        if data:
            return data["connections"]
        else:
            return

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

    def get_all_airports(self):
        return [airport['airport_code'] for airport in self.airport_collection.find()]

    def add_connections_to_area(self, area, connections):
        self.connections_collection.update({"area": area}, {"$push": {"connections": connections}}, upsert=True)

    def get_connections_in_area(self, area):
        data = self.connections_collection.find_one({"area": area})
        if data:
            return data["connections"]
        else:
            return

    def clean_areas_to_connections_table(self):
        self.connections_collection.remove()

    def get_area_code(self, origin, dest):
        origin_area = self.airport_collection.find_one({"airport_code": origin})
        dest_area = self.airport_collection.find_one({"airport_code": dest})

        if origin_area and dest_area:
            return "%s-%s" % (origin_area["area"], dest_area["area"])
        else:
            return