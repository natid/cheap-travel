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

        if trip_data and trip_data.has_key("Journeys") and trip_data['Journeys'] and len(trip_data['Journeys']) > 0:
            return self.flights_provider.extract_cheapest_price(trip_data), trip_data

        return (None, None)

    def get_price_one_way(self, origin, dest, depart_dates):
        first_trip = self.flights_provider.build_trip(origin, dest, depart_dates, 1)
        trip_data = self.flights_provider.get_flights_info([first_trip])

        if trip_data and trip_data.has_key("Journeys") and len(trip_data['Journeys']) > 0:
            return self.flights_provider.extract_cheapest_price(trip_data), trip_data

        return (None, None)


