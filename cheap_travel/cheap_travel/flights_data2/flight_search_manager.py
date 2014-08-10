from collections import defaultdict
from threading import Thread
import threading
from flights_data2.connection_flight_checks.connection_flight_types import ConnectionFlightTypes
from flights_data2.connection_flight_checks.flight_types import TwoOneWaysFlightType, RoundTripFlightType
from flights_data2.observer import Observable
import time
from constants import PENDING, ERROR_RESPONSE

CONNECTION_KEY_SEPERATOR = "$"

class FlightPricesData(object):

    def __init__(self):
        self.trip_to_prices = {}
        self.cheapest_price = None

    def add_trip(self, trip, price):
        self.trip_to_prices[trip] = price

    def calculate_cheapest_flight(self):
        if self.trip_to_prices:
            trips = self.trip_to_prices.items()
            self.cheapest_price = min(trips, key=lambda x:x[1])

    def get_cheapest_price(self):
        self.calculate_cheapest_flight()
        return self.cheapest_price


class FlightSearchManager(Observable):

    def __init__(self, trip_data, flight_provider, flights_resp_dal, thread_pool):
        super(FlightSearchManager, self).__init__()
        self.trip_data = trip_data
        self.origin = trip_data.origin
        self.dest = trip_data.dest
        self.depart_date = trip_data.depart_dates[0]
        if trip_data.return_dates:
            self.return_date = trip_data.return_dates[0]
        self.flights_resp_dal = flights_resp_dal
        self.flight_provider = flight_provider
        self.flights_prices_data = defaultdict(dict)
        self.pool = thread_pool
        self.connection_flight_data = {}
        self.unfinished_requests = []
        self.cheapest_flight = None
        self.mutex = threading.RLock()


    def search_all_flight_combinations(self):
        area = self.flights_resp_dal.get_area_code(self.origin, self.dest)
        #TODO - don't forget to uncomment this after the connection list is ok
        #connections_list = self.flights_resp_dal.get_connections_in_area(area)
        connections_list = "AMS","CDG"
        if len(connections_list) == 0:
            print "couldn't get connection list"
            return None

        self.search_base_trips_flight()
        self.send_requests_to_flight_provider(connections_list)
        self.update_responses()
        self.notify_observers(finished=True)


    def search_base_trips_flight(self):
        t_round_trip = Thread(target=self.search_round_trip)
        t_round_trip.start()

        t_two_one_ways = Thread(target=self.search_two_one_ways)
        t_two_one_ways.start()

    def search_round_trip(self):
        self.round_trip_flight = RoundTripFlightType(self.trip_data)
        response = self.flight_provider.search_flight(self.trip_data)

        if response and response != ERROR_RESPONSE:
            self.round_trip_flight.set_trip_data_response(self.trip_data.compute_key(), response)
            self.notify_if_cheaper(self.round_trip_flight)

    def search_two_one_ways(self):
        two_one_ways_trip_flight = TwoOneWaysFlightType(self.trip_data)
        flights_to_search = two_one_ways_trip_flight.get_trip_data_requests()

        flight1 = flights_to_search[0]
        flight2 = flights_to_search[1]

        response1 = self.flight_provider.search_flight(flight1)
        response2 = self.flight_provider.search_flight(flight2)

        if response1 and response1 != ERROR_RESPONSE and response2 and response2 != ERROR_RESPONSE:
            two_one_ways_trip_flight.set_trip_data_response(flight1.compute_key(), response1)
            two_one_ways_trip_flight.set_trip_data_response(flight2.compute_key(), response2)
            self.notify_if_cheaper(two_one_ways_trip_flight)

    def notify_if_cheaper(self, flight_type):
        self.mutex.acquire()
        try:
            updated_flight_data = flight_type.get_final_price()
            if (self.cheapest_flight is None and updated_flight_data[0]) or (updated_flight_data[0] and updated_flight_data[0] < self.cheapest_flight[0]):
                self.cheapest_flight = updated_flight_data
                self.notify_observers(flight_type=flight_type)
        finally:
            self.mutex.release()

    def build_flights_prices_data(self ,connections_list):
        for single_connection in connections_list:
            self.flights_prices_data[single_connection] = {}


    def send_requests_to_flight_provider(self, connections_list):
        for single_connection in connections_list:
            connection_flight_types = ConnectionFlightTypes(self.trip_data, single_connection)
            trips_data_and_flight_types = connection_flight_types.get_flights_for_connection()
            for flight_type, trips_data in trips_data_and_flight_types:
                for trip_data in trips_data:
                    self.pool.add_task(self.flight_provider.search_flight, trip_data)
                    key = CONNECTION_KEY_SEPERATOR.join([single_connection, trip_data.compute_key()])
                    self.connection_flight_data[key] = flight_type

    def get_flight_provider_request_list(self, connection):
        return [
                    (self.origin, self.dest, self.depart_date, self.return_date), # roundtrip
                    (self.origin, self.dest, self.depart_date), # two one ways
                    (self.dest, self.dest, self.depart_date), # two one ways

        ]

    def update_responses(self):
        self.unfinished_requests = self.connection_flight_data.keys()
        while self.unfinished_requests:
            for request in self.unfinished_requests[:]:
                connection, trip_key = request.split(CONNECTION_KEY_SEPERATOR)
                response = self.flights_resp_dal.get(trip_key)
                if response and response != PENDING:
                    self.unfinished_requests.remove(request)
                    self.connection_flight_data[request].set_trip_data_response(trip_key, response)
                    self.notify_if_cheaper(self.connection_flight_data[request])

            time.sleep(1)


    def get_cheapest_flight(self):
        return self.cheapest_flight

    def is_finished(self):
        return bool(self.unfinished_requests)

