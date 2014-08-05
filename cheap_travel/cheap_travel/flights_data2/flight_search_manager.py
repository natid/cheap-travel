from collections import defaultdict
from flights_data2.connection_flight_checks.connection_flight_types import ConnectionFlightTypes
from flights_data2.thread_pool2 import ThreadPool


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


class FlightSearchManager(object):

    def __init__(self, trip_data, flight_provider, flights_resp_dal):
        self.trip_data = trip_data
        self.origin = trip_data['origin']
        self.dest = trip_data['dest']
        self.depart_date = trip_data['depart_dates'][0]
        self.return_date = trip_data['return_dates'][0]
        self.flights_resp_dal = flights_resp_dal
        self.flight_provider = flight_provider
        self.flights_prices_data = defaultdict(dict)
        self.pool = ThreadPool(20)


    def search_flight(self):
        area = self.flights_resp_dal.get_area_code(self.origin, self.dest)
        connections_list = self.flights_resp_dal.get_connections_in_area(area)

        if len(connections_list) == 0:
            print "couldn't get connection list"
            return None

        self.send_requests_to_flight_provider(connections_list)


    def build_flights_prices_data(self ,connections_list):
        for single_connection in connections_list:
            self.flights_prices_data[single_connection] = {}


    def send_requests_to_flight_provider(self, connections_list):
        for single_connection in connections_list:
            connectionFlightData = ConnectionFlightTypes(self.trip_data, single_connection)
            trips_data = connectionFlightData.get_flights_for_connection()
            for trip_data in trips_data:
                self.pool.add_task(self.flight_provider.search_flight, trip_data)
            # TODO build data structure



    '''
    def later(self):
        for single_connection in connections_list:
            if origin != dest != single_connection != origin:
                async_response = self.flight_checker.run_test_list(origin, dest, depart_date, return_date, single_connection, None)
                self.resp_collector.add_response(single_connection, "first", async_response)
    '''
    def get_flight_provider_request_list(self, connection):
        return [
                    (self.origin, self.dest, self.depart_date, self.return_date), # roundtrip
                    (self.origin, self.dest, self.depart_date), # two one ways
                    (self.dest, self.dest, self.depart_date), # two one ways


        ]

    def get_roundtrip_requests():

