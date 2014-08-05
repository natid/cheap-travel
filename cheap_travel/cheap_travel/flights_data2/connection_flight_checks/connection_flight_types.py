from flights_data2.connection_flight_checks.flight_types import ConnectionInTheBeginningFlightType, \
    ConnectionInTheEndFlightType, TwoConnectionsStayInTheBeginningFlightType, TwoConnectionsStayInTheEndFlightType


class ConnectionFlightTypes(object):

    def __init__(self, original_trip_data, connection=None):
        self.original_trip_data = original_trip_data
        self.origin = original_trip_data.origin
        self.dest = original_trip_data.dest
        self.depart_date = original_trip_data.depart_dates[0]
        self.return_date = original_trip_data.return_dates[0]
        self.connection = connection

        self.flight_types = [
            ConnectionInTheBeginningFlightType(original_trip_data, connection),
            ConnectionInTheEndFlightType(original_trip_data, connection),
            TwoConnectionsStayInTheBeginningFlightType(original_trip_data, connection),
            TwoConnectionsStayInTheEndFlightType(original_trip_data, connection)
        ]

    def get_flights_for_connection(self):
        flights = []
        for flight_type in self.flight_types:
            flights.extend(flight_type.get_relevant_trip_data())

        return flights