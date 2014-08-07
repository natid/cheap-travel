from flights_data2.connection_flight_checks.flight_types import ConnectionInTheBeginningFlightType, \
    ConnectionInTheEndFlightType, TwoConnectionsStayInTheBeginningFlightType, TwoConnectionsStayInTheEndFlightType


class ConnectionFlightTypes(object):

    def __init__(self, trip_data_request, connection=None):
        self.original_trip_data = trip_data_request
        self.connection = connection

        self.flight_types = [
            ConnectionInTheBeginningFlightType(trip_data_request, connection),
            ConnectionInTheEndFlightType(trip_data_request, connection),
            TwoConnectionsStayInTheBeginningFlightType(trip_data_request, connection),
            TwoConnectionsStayInTheEndFlightType(trip_data_request, connection)
        ]

    def get_flights_for_connection(self):
        flights_requests = []
        for flight_type in self.flight_types:
            flights_requests.append((flight_type, flight_type.get_trip_data_requests()))

        return flights_requests