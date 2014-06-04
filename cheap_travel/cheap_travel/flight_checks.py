from flights_data.pricer import Pricer
import utils
from datetime import date, timedelta, datetime
import time
from dateutil import parser


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
            price3, trip_data3 = get_cheapest_flight_and_price(trip_data3)
            price1, trip_data1, price2, trip_data2 = get_cheapest_flights_that_can_connect(True, trip_data1, trip_data2)
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
            price1, trip_data1 = get_cheapest_flight_and_price(trip_data1)
            price2, trip_data2, price3, trip_data3 = get_cheapest_flights_that_can_connect(True, trip_data2, trip_data3)
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
            price1, trip_data1, price2, trip_data2 = get_cheapest_flights_that_can_connect(False, trip_data1, trip_data2)
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
            price1, trip_data1, price2, trip_data2 = get_cheapest_flights_that_can_connect(False, trip_data1, trip_data2)
            return ("Two Connections stay in the end in {} at {}".format(connection, utils.get_return_flight_date(trip_data1)), price1 + price2,[trip_data1, trip_data2] )
        else:
            return None

def get_cheapest_flights_that_can_connect(is_one_way_flights, trip1, trip2):

    return utils.extract_cheapest_price(trip1['Journeys'][0][0]), trip1['Journeys'][0][0], \
           utils.extract_cheapest_price(trip2['Journeys'][0][0]), trip2['Journeys'][0][0]

    #TODO - make an smart algorithm to find the cheapest combination -
    #Note -  it might be good to use iterations according to the jumps on prices

    # if is_one_way_flights:
    #     for first_flight in trip1['Journeys']:
    #         for second_flight in trip2['Journeys']:
    #             if flights_can_connect(first_flight["Flights"][-1], second_flight["Flights"][0]):
    #                 return utils.extract_cheapest_price(first_flight), first_flight, \
    #                        utils.extract_cheapest_price(second_flight), second_flight
    # else:
    #     pass

def get_cheapest_flight_and_price(trip_data):
    sorted_trips = sorted(trip_data['Journeys'], key=lambda trip: trip[0]['Price']['Total']['Amount'])
    try:
        return sorted_trips[0][0]['Price']['Total']['Amount'],sorted_trips[0][0]
    except:
        print "ERROR getting the cheapest flight" , trip_data, sorted_trips
        return (None, None)

def flights_can_connect(flight1, flight2):
    #first check that it's the same airport
    #TODO - see how we handle airport changes in the connections
    if(flight1["Destination"] != flight2["Origin"]):
        return False

    #then check that there's a 5 hour connection time (#TODO - why 5?)
    arrival_time = parser.parse(flight1["Arrival"])
    deparure_time = parser.parse(flight2["Departure"])
    delta = deparure_time - arrival_time

    if(delta.total_seconds()/60/60  < 5):
        return False

    return True
