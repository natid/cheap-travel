from datetime import timedelta
from flights_data2.connection_flight_checks.base_flight_type import BaseFlightType
from flights_data2.constants import CONNECTION_DAYS


class RoundTripFlightType(BaseFlightType):

    def calculate_relevant_flights(self):
        self.set_flight_trip_data("first", self.original_trip_data)

    def get_final_price(self):
        price, trip_data = self.get_flight_price_data("first")
        if price:
            return ("Round Trip", price, [trip_data])
        else:
            return None


class TwoOneWaysFlightType(BaseFlightType):

    def calculate_relevant_flights(self):
        self.set_flight_trip_data("first", (self.origin, self.dest, self.depart_date))
        self.set_flight_trip_data("second", (self.origin, self.dest, self.depart_date))

    def get_final_price(self):
        price1, trip_data1 = self.get_flight_price_data("first")
        price2, trip_data2 = self.get_flight_price_data("second")
        if price1 and price2:
            return ( "Two one ways", price1 + price2, [trip_data1, trip_data2])
        else:
            return None


class ConnectionInTheBeginningFlightType(BaseFlightType):

    def calculate_relevant_flights(self):
        self.set_flight_trip_data("first", (self.origin, self.dest, self.depart_date))
        self.set_flight_trip_data("second", (self.origin, self.dest, self.depart_date))

        depart_dates = []
        for i in range(CONNECTION_DAYS):
            depart_from_dest_date = return_date - timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_dest_date))


        response1 = self.pricer.get_price_one_way(origin, connection1, self._create_str_date(depart_date))
        response2 = self.pricer.get_price_one_way(connection1, dest, depart_dates)
        response3 = self.pricer.get_price_one_way(dest, origin, self._create_str_date(return_date))


class ConnectionInTheEndFlightType(BaseFlightType):
    pass

class TwoConnectionsStayInTheBeginningFlightType(BaseFlightType):
    pass

class TwoConnectionsStayInTheEndFlightType(BaseFlightType):
    pass
