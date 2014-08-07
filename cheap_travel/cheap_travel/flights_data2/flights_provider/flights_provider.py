import time
from constants import PENDING, ERROR_RESPONSE
import traceback

class BaseFlightsProvider(object):
    
    def __init__(self, flights_resp_dal):
        self.flights_resp_dal = flights_resp_dal

    def search_flight(self, trip_data):
        key = trip_data.compute_key()
        cached_resp = self.get_flight_from_cache(key)
        if cached_resp:
            return cached_resp

        try:
            self.flights_resp_dal.set(key, PENDING)
            flight_data = self.call_provider(self.build_trip_request(trip_data))
            if not flight_data:
                self.flights_resp_dal.set(key, ERROR_RESPONSE)
                return
        except Exception as e:
            traceback.print_exc()
            print e
            self.flights_resp_dal.set(key, ERROR_RESPONSE)
            return

        data_to_save = self.convert_provider_response(flight_data)
        self.save_flight_to_db(key, data_to_save)
        return cached_resp

    def get_flight_from_cache(self, key):
        cached_resp = self.flights_resp_dal.get(key)
        while self.flights_resp_dal.has_key(key) and cached_resp is None:
            time.sleep(5)
            cached_resp = self.flights_resp_dal.get(key)
        return cached_resp

    def save_flight_to_db(self, key, res):
        self.flights_resp_dal.set(key, res)

    def call_provider(self, trip):
        pass

    def convert_provider_response(self, flight_data):
        pass

    def build_trip_request(self, trip_data):
        pass
