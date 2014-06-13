from vayant import VayantConnector

class Pricer(object):

    def __init__(self, provider):
        if provider == "Vayant":
            self.flights_provider = VayantConnector()
        else:
            assert False

    def get_price_round_trip(self, origin, dest, depart_dates, arrive_dates, get_full_response = False):
        first_trip = self.flights_provider.build_trip(origin, dest, depart_dates, 1)
        second_trip = self.flights_provider.build_trip(dest, origin, arrive_dates, 2)
        trip_data = self.flights_provider.get_flights_info([first_trip, second_trip])

        if not trip_data:
            return (None, None)

        trip_to_return = trip_data if get_full_response else self.flights_provider.get_first_flight_from_trip(trip_data)
        return self.flights_provider.extract_cheapest_price(trip_data), trip_to_return

    def get_price_one_way(self, origin, dest, depart_dates, get_full_response = False):
        first_trip = self._build_trip(origin, dest, depart_dates, 1)
        trip_data = self.vayant_connector.call_vayant([first_trip])

        if not trip_data:
            return (None, None)

        trip_to_return = trip_data if get_full_response else self.flights_provider.get_first_flight_from_trip(trip_data)
        return self.flights_provider.extract_cheapest_price(trip_data), trip_to_return

