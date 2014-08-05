from flights_data2.trip_data import TripData


class BaseFlightType(object):
    def __init__(self, original_trip_data, connection=None):
        self.original_trip_data = original_trip_data
        self.origin = original_trip_data.origin
        self.dest = original_trip_data.dest
        self.depart_date = original_trip_data.depart_dates[0]
        self.return_date = original_trip_data.return_dates[0]
        self.connection = connection
        self.relevant_flights = {}
        self.name_to_key = {}
        self.calculate_relevant_flights()

    def get_flight_price_data(self, name):
        return self.relevant_flights[self.name_to_key[name]]

    def get_relevant_trip_keys(self):
        return self.relevant_flights.keys()

    def get_relevant_trip_data(self):
        return [trip_and_price[1] for trip_and_price in self.relevant_flights.values()]

    def set_flight_price(self, key, price):
        self.relevant_flights[key][0] = price

    def set_flight_trip_data(self, name, trip_data):
        self.name_to_key[name] = trip_data.compute_key
        self.relevant_flights[trip_data.compute_key] = (None, TripData(*trip_data))

    def calculate_relevant_flights(self):
        pass

    def get_final_price(self):
        pass


