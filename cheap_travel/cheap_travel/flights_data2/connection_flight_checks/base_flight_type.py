from flights_data2.trip_data import TripDataRequest, TripDataResponse
from constants import ERROR_RESPONSE, MAX_FLIGHTS_PER_TRIP
class BaseFlightType(object):

    # These are the 3 functions that the inheriting class should implement
    def calculate_relevant_flights(self):
        raise NotImplemented

    def get_final_price(self):
        raise NotImplemented

    def get_flight_type_str(self):
        raise NotImplemented

    def __init__(self, original_trip_data, connection=None):
        self.original_trip_data = original_trip_data
        self.origin = original_trip_data.origin
        self.dest = original_trip_data.dest
        self.depart_date = original_trip_data.depart_dates[0]
        if original_trip_data.return_dates:
            self.return_date = original_trip_data.return_dates[0]
        self.connection = connection
        self.relevant_requests = []
        self.relevant_responses = {}
        self.name_to_key = {}
        self.calculate_relevant_flights()

    def get_trip_data_response(self, name):
        if self.name_to_key[name] in self.relevant_responses.keys():
            return self.relevant_responses[self.name_to_key[name]]
        return None

    def set_trip_data_response(self, key, trip_data_response):
        if trip_data_response and trip_data_response != ERROR_RESPONSE:
            self.relevant_responses[key] = TripDataResponse(trip_data_response)

    def get_trip_data_requests(self):
        return self.relevant_requests

    def set_trip_data_request(self, name, trip_data_request):
        request = TripDataRequest(*trip_data_request)
        self.name_to_key[name] = request.compute_key()
        self.relevant_requests.append(request)

    def get_cheapest_flights_that_can_connect(self, is_one_way_flights, response1, response2, connection):
        cookie = [0 for _ in range(4)]
        first_flight, second_flight = self._get_next_flights(response1, response2, cookie)
        while first_flight and second_flight:
            if is_one_way_flights:
                if first_flight.legs[-1].flights_can_connect(second_flight.legs[0]):
                    return first_flight.price, first_flight, second_flight.price, second_flight
            else:
                connection_arrival, connection_departure = first_flight.get_dest_arrival_and_departure_flights_in_two_way(connection)
                if connection_arrival and connection_arrival.flights_can_connect(second_flight.legs[0]) and \
                   second_flight.legs[-1].flights_can_connect(connection_departure):

                    return first_flight.price, first_flight, second_flight.price, second_flight

            first_flight, second_flight = self._get_next_flights(response1, response2, cookie)
        return None, None, None ,None

    def _get_next_flights(self, response1, response2, cookie):
        found, first_index, second_index, first_base_index, second_base_index = self._get_next_indexes(cookie, response1, response2)
        if not found:
            return None, None
        cookie[:4] = first_index, second_index, first_base_index, second_base_index
        return response1.trips[first_index], response2.trips[second_index]

    def _get_next_indexes(self, cookie, response1, response2):
        update_second = False
        first_jump_price = second_jump_price = 0

        first_index, second_index, first_base_index, second_base_index = cookie

        if first_index == MAX_FLIGHTS_PER_TRIP - 1:
            if second_index == MAX_FLIGHTS_PER_TRIP - 1:
                return False, None, None, None, None
            update_second = True

        elif second_index != MAX_FLIGHTS_PER_TRIP - 1:
            first_jump_price = response1.trips[first_index + 1].price - response1.trips[first_base_index].price

            second_jump_price = response2.trips[second_index + 1].price - response2.trips[second_base_index].price

        if first_jump_price < second_jump_price or not update_second:
            first_index += 1
            second_base_index += 1
            second_index = second_base_index
        else:
            second_index += 1
            first_base_index += 1
            first_index = first_base_index

        return True, first_index, second_index, first_base_index, second_base_index