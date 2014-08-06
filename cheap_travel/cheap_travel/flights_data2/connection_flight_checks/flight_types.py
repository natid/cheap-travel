from datetime import timedelta
from flights_data2.connection_flight_checks.base_flight_type import BaseFlightType
from flights_data2.constants import CONNECTION_DAYS


class RoundTripFlightType(BaseFlightType):

    def calculate_relevant_flights(self):
        self.set_flight_trip_data("first", (self.origin, self.dest, self.depart_date, self.return_date))

    def get_final_price(self):
        cheapest_price1, cheapest_flight1 = self.get_trip_data_response("first").get_cheapest_flight_and_price()
        return (cheapest_price1, [cheapest_flight1])

    def get_flight_type_str(self):
        return "Round Trip"

class TwoOneWaysFlightType(BaseFlightType):

    def calculate_relevant_flights(self):
        self.set_flight_trip_data("first", (self.origin, self.dest, self.depart_date))
        self.set_flight_trip_data("second", (self.dest, self.origin, self.return_date))

    def get_final_price(self):
        cheapest_price1, cheapest_flight1 = self.get_trip_data_response("first").get_cheapest_flight_and_price()
        cheapest_price2, cheapest_flight2 = self.get_trip_data_response("second").get_cheapest_flight_and_price()
        return (cheapest_price1 + cheapest_price2, [cheapest_flight1, cheapest_flight2])

    def get_flight_type_str(self):
        return "Two one ways"

class ConnectionInTheBeginningFlightType(BaseFlightType):

    def calculate_relevant_flights(self):
        depart_dates = [self.depart_date + timedelta(days=i) for i in range(CONNECTION_DAYS)]

        self.set_flight_trip_data("first", (self.origin, self.connection, self.depart_date))
        self.set_flight_trip_data("second", (self.connection, self.dest, depart_dates))
        self.set_flight_trip_data("third", (self.dest, self.origin, self.return_date))

    def get_final_price(self):
        trip_data_response1 = self.get_trip_data_response("first")
        trip_data_response2 = self.get_trip_data_response("second")
        trip_data_response3 = self.get_trip_data_response("third")

        if trip_data_response1 and trip_data_response2 and trip_data_response3:
            cheapest_flight1, cheapest_price1, cheapest_flight2, cheapest_price2 = \
                self.get_cheapest_flights_that_can_connect(True, trip_data_response1, trip_data_response2, self.connection)

            cheapest_flight3, cheapest_price3 = trip_data_response3.get_cheapest_flight_and_price()

            if cheapest_flight1 and cheapest_flight2 and cheapest_flight3:
                return (cheapest_price1 + cheapest_price2 + cheapest_price3, [cheapest_flight1, cheapest_flight2, cheapest_flight3] )

        return None, None

    def get_flight_type_str(self):
        return "Connection at the beginning at {}".format(self.connection)

class ConnectionInTheEndFlightType(BaseFlightType):

    def calculate_relevant_flights(self):
        depart_dates = [self.return_date - timedelta(days=i) for i in range(CONNECTION_DAYS)]

        self.set_flight_trip_data("first", (self.origin, self.dest, self.depart_date))
        self.set_flight_trip_data("second", (self.dest, self.connection, depart_dates))
        self.set_flight_trip_data("third", (self.connection, self.origin, self.return_date))

    def get_final_price(self):
        trip_data_response1 = self.get_trip_data_response("first")
        trip_data_response2 = self.get_trip_data_response("second")
        trip_data_response3 = self.get_trip_data_response("third")

        if trip_data_response1 and trip_data_response2 and trip_data_response3:
            cheapest_flight1, cheapest_price1 = trip_data_response1.get_cheapest_flight_and_price()

            cheapest_flight2, cheapest_price2, cheapest_flight3, cheapest_price3 = \
                self.get_cheapest_flights_that_can_connect(True, trip_data_response2, trip_data_response3, self.connection)

            if cheapest_flight1 and cheapest_flight2 and cheapest_flight3:
                return (cheapest_price1 + cheapest_price2 + cheapest_price3, [cheapest_flight1, cheapest_flight2, cheapest_flight3] )

        return None, None

    def get_flight_type_str(self):
        return "Connection in the end at {}".format(self.connection)

class TwoConnectionsStayInTheBeginningFlightType(BaseFlightType):

    def calculate_relevant_flights(self):
        depart_dates = [self.depart_date + timedelta(days=i) for i in range(CONNECTION_DAYS)]

        self.set_flight_trip_data("first", (self.origin, self.connection, self.depart_date, self.return_date))
        self.set_flight_trip_data("second", (self.connection, self.dest, depart_dates, self.return_date))

    def get_final_price(self):
        trip_data_response1 = self.get_trip_data_response("first")
        trip_data_response2 = self.get_trip_data_response("second")

        if trip_data_response1 and trip_data_response2:
            cheapest_flight1, cheapest_price1, cheapest_flight2, cheapest_price2 = \
                self.get_cheapest_flights_that_can_connect(False, trip_data_response1, trip_data_response2, self.connection)

            if cheapest_flight1 and cheapest_flight2:
                return (cheapest_price1 + cheapest_price2, [cheapest_flight1, cheapest_flight2] )

        return None, None

    def get_flight_type_str(self):
        return "Two Connections stay in the beginning at {}".format(self.connection)


class TwoConnectionsStayInTheEndFlightType(BaseFlightType):
    def calculate_relevant_flights(self):
        depart_dates = [self.return_date - timedelta(days=i) for i in range(CONNECTION_DAYS)]

        self.set_flight_trip_data("first", (self.origin, self.connection, self.depart_date, self.return_date))
        self.set_flight_trip_data("second", (self.connection, self.dest, depart_dates, self.return_date))

    def get_final_price(self):
        trip_data_response1 = self.get_trip_data_response("first")
        trip_data_response2 = self.get_trip_data_response("second")

        if trip_data_response1 and trip_data_response2:
            cheapest_flight1, cheapest_price1, cheapest_flight2, cheapest_price2 = \
                self.get_cheapest_flights_that_can_connect(False, trip_data_response1, trip_data_response2, self.connection)

            if cheapest_flight1 and cheapest_flight2:
                return (cheapest_price1 + cheapest_price2, [cheapest_flight1, cheapest_flight2] )

        return None, None

    def get_flight_type_str(self):
        return "Two Connections stay in the end at {}".format(self.connection)