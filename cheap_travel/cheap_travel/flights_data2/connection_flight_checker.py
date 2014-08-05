from datetime import timedelta
from constants import CONNECTION_DAYS


class ConnectionFlightChecker(object):

    def __init__(self, trip_data, connection):
        self.trip_data = trip_data
        self.connection = connection
        self.origin = trip_data['origin']
        self.dest = trip_data['dest']
        self.depart_date = trip_data['depart_dates'][0]
        self.return_date = trip_data['return_dates'][0]

        (self.check_connection_in_the_beginning,
                self.check_connection_in_the_end,
                self.check_two_connections_stay_in_the_beginning,
                self.check_two_connections_stay_in_the_end)

    def get_flights_to_check(self):
        flights_to_check = []
        flights_to_check.extend(self.get_connection_in_the_beginning_flights())
        flights_to_check.extend(self.get_connection_in_the_end_flights())
        flights_to_check.extend(self.get_two_connections_stay_in_the_beginning_flights())
        flights_to_check.extend(self.get_two_connections_stay_in_the_end_flights())

        return flights_to_check

    def get_connection_in_the_beginning_flights(self):
        depart_dates = []
        for i in range(CONNECTION_DAYS):
            depart_from_connection_date = self.depart_date + timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_connection_date))

        return [(self.origin, self.connection, self._create_str_date(self.depart_date)),
                (self.connection, self.dest, depart_dates),
                (self.dest, self.origin, self._create_str_date(self.return_date))]

    def get_connection_in_the_end_flights(self):
        depart_dates = []
        for i in range(CONNECTION_DAYS):
            depart_from_dest_date = self.return_date - timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_dest_date))

        return [(self.origin, self.dest, self._create_str_date(self.depart_date)),
                (self.dest, self.connection, depart_dates),
                (self.connection, self.origin, self._create_str_date(self.return_date))]


    def get_two_connections_stay_in_the_beginning_flights(self):
        depart_dates = []
        for i in range(CONNECTION_DAYS):
            depart_from_connection_date = self.depart_date + timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_connection_date))

        return [(self.origin, self.connection, self._create_str_date(self.depart_date),self._create_str_date(self.return_date)),
                (self.connection1, self.dest, depart_dates, self._create_str_date(self.return_date))]


    def get_two_connections_stay_in_the_end_flights(self):
        return_dates = []
        for i in range(CONNECTION_DAYS):
            depart_from_dest_date = self.return_date - timedelta(days=i)
            return_dates.append(self._create_str_date(depart_from_dest_date))

        return [(self.origin, self.connection, self._create_str_date(self.depart_date), self._create_str_date(self.return_date)),
                (self.connection, self.dest, self._create_str_date(self.depart_date), return_dates)]


