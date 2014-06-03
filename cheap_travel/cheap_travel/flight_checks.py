from cheap_travel.flights_data.pricer import Pricer
import utils
from datetime import date, timedelta


class FlightChecker(object):
    def __init__(self):
        self.pricer = Pricer()

    def check_round_trip(self, origin, dest, depart_date, return_date, connection):
        price, round_trip_data = self.pricer.get_price_round_trip(origin, dest, utils._create_str_date(depart_date), utils._create_str_date(return_date))
        if price:
            return ("Round Trip", price, [round_trip_data])
        else:
            return None

    def check_two_one_ways(self, origin, dest, depart_date, return_date, connection):
        price1, trip_data1 = self.pricer.get_price_one_way(origin, dest, utils._create_str_date(depart_date))
        price2, trip_data2 = self.pricer.get_price_one_way(dest, origin, utils._create_str_date(return_date))

        if price1 and price2:
            return ( "Two one ways",price1+price2,[trip_data1, trip_data2])
        else:
            return None

    def check_connection_in_the_beginning(self, origin, dest, depart_date, return_date, connection):
        depart_dates = []
        for i in range(4):
            depart_from_connection_date = depart_date + timedelta(days=i)
            depart_dates.append(utils._create_str_date(depart_from_connection_date))

        price1, trip_data1 = self.pricer.get_price_one_way(origin, connection, utils._create_str_date(depart_date))
        price2, trip_data2 = self.pricer.get_price_one_way(connection, dest, depart_dates)
        price3, trip_data3 = self.pricer.get_price_one_way(dest, origin, utils._create_str_date(return_date))

        if price1 and price2 and price3 :
            return ("Connection in beginning in {} at {}".format(connection, utils.get_departure_flight_date(trip_data2)), price1 + price2 + price3, [trip_data1, trip_data2, trip_data3] )
        else:
            return None

    def check_connection_in_the_end(self, origin, dest, depart_date, return_date, connection):
        depart_dates = []
        for i in range(4):
            depart_from_dest_date = return_date - timedelta(days=i)
            depart_dates.append(utils._create_str_date(depart_from_dest_date))

        price1, trip_data1 = self.pricer.get_price_one_way(origin, dest, utils._create_str_date(depart_date))
        price2, trip_data2 = self.pricer.get_price_one_way(dest, connection , depart_dates)
        price3, trip_data3 = self.pricer.get_price_one_way(connection, origin, utils._create_str_date(return_date))

        if price1 and price2 and price3 :
            return ("Connection in the end in {} at {}".format(connection, utils.get_departure_flight_date(trip_data2)), price1 + price2 + price3, [trip_data1, trip_data2, trip_data3] )
        else:
            return None

    def check_two_connections_stay_in_the_beginning(self, origin, dest, depart_date, return_date, connection):
        depart_dates = []
        for i in range(4):
            depart_from_connection_date = depart_date + timedelta(days=i)
            depart_dates.append(utils._create_str_date(depart_from_connection_date))

        price1, trip_data1 = self.pricer.get_price_round_trip(origin, connection, utils._create_str_date(depart_date), utils._create_str_date(return_date))
        price2, trip_data2 = self.pricer.get_price_round_trip(connection, dest, depart_dates, utils._create_str_date(return_date))
        if price1 and price2 :
            return ("Two Connections stay in the beginning in {} at {}".format(connection, utils.get_departure_flight_date(trip_data2)), price1 + price2, [trip_data1, trip_data2]  )
        else:
            return None

    def check_two_connections_stay_in_the_end(self, origin, dest, depart_date, return_date, connection):
        depart_dates = []
        for i in range(4):
            depart_from_dest_date = return_date - timedelta(days=i)
            depart_dates.append(utils._create_str_date(depart_from_dest_date))

        price1, trip_data1 = self.pricer.get_price_round_trip(origin, connection, utils._create_str_date(depart_date), depart_dates)
        price2, trip_data2 = self.pricer.get_price_round_trip(connection, dest, utils._create_str_date(depart_date), utils._create_str_date(return_date))
        if price1 and price2 :
            return ("Two Connections stay in the end in {} at {}".format(connection, utils.get_return_flight_date(trip_data1)), price1 + price2,[trip_data1, trip_data2] )
        else:
            return None
