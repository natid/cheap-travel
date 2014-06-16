from datetime import timedelta

from pricer import Pricer

from dateutil import parser
import constants
from pprint import pprint

class FlightChecker(object):
    def __init__(self):
        self.pricer = Pricer("Vayant")

    def check_round_trip(self, origin, dest, depart_date, return_date, connection):
        price1, trip_data1 = self.pricer.get_price_round_trip(origin, dest, self._create_str_date(depart_date),
                                                              self._create_str_date(return_date))
        if price1:
            price1, trip_data1 = self.get_cheapest_flight_and_price(trip_data1)
            return ("Round Trip", price1, [trip_data1])
        else:
            return None

    def check_two_one_ways(self, origin, dest, depart_date, return_date, connection):
        price1, trip_data1 = self.pricer.get_price_one_way(origin, dest, self._create_str_date(depart_date))
        price2, trip_data2 = self.pricer.get_price_one_way(dest, origin, self._create_str_date(return_date))

        if price1 and price2:
            price1, trip_data1 = self.get_cheapest_flight_and_price(trip_data1)
            price2, trip_data2 = self.get_cheapest_flight_and_price(trip_data2)
            return ( "Two one ways", price1 + price2, [trip_data1, trip_data2])
        else:
            return None

    def check_connection_in_the_beginning(self, origin, dest, depart_date, return_date, connection):
        depart_dates = []
        for i in range(4):
            depart_from_connection_date = depart_date + timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_connection_date))

        price1, trip_data1 = self.pricer.get_price_one_way(origin, connection, self._create_str_date(depart_date))
        price2, trip_data2 = self.pricer.get_price_one_way(connection, dest, depart_dates)
        price3, trip_data3 = self.pricer.get_price_one_way(dest, origin, self._create_str_date(return_date))

        if price1 and price2 and price3:
            price3, trip_data3 = self.get_cheapest_flight_and_price(trip_data3)
            price1, trip_data1, price2, trip_data2 = self.get_cheapest_flights_that_can_connect(True, trip_data1,
                                                                                                trip_data2)
            if price1 and price2:
                return ("Connection in beginning in {} at {}".format(connection,
                                                                     self.pricer.flights_provider.get_departure_flight_date(
                                                                         trip_data2)), price1 + price2 + price3,
                        [trip_data1, trip_data2, trip_data3] )
        return None

    def check_connection_in_the_end(self, origin, dest, depart_date, return_date, connection):
        depart_dates = []
        for i in range(4):
            depart_from_dest_date = return_date - timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_dest_date))

        price1, trip_data1 = self.pricer.get_price_one_way(origin, dest, self._create_str_date(depart_date))
        price2, trip_data2 = self.pricer.get_price_one_way(dest, connection, depart_dates)
        price3, trip_data3 = self.pricer.get_price_one_way(connection, origin, self._create_str_date(return_date))

        if price1 and price2 and price3:
            price1, trip_data1 = self.get_cheapest_flight_and_price(trip_data1)
            price2, trip_data2, price3, trip_data3 = self.get_cheapest_flights_that_can_connect(True, trip_data2,
                                                                                                trip_data3)
            if price2 and price3:
                return ("Connection in the end in {} at {}".format(connection,
                                                                   self.pricer.flights_provider.get_departure_flight_date(
                                                                       trip_data2)), price1 + price2 + price3,
                        [trip_data1, trip_data2, trip_data3] )
        return None

    def check_two_connections_stay_in_the_beginning(self, origin, dest, depart_date, return_date, connection):
        depart_dates = []
        for i in range(4):
            depart_from_connection_date = depart_date + timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_connection_date))

        price1, trip_data1 = self.pricer.get_price_round_trip(origin, connection, self._create_str_date(depart_date),
                                                              self._create_str_date(return_date))
        price2, trip_data2 = self.pricer.get_price_round_trip(connection, dest, depart_dates,
                                                              self._create_str_date(return_date))
        if price1 and price2:
            price1, trip_data1, price2, trip_data2 = self.get_cheapest_flights_that_can_connect(False, trip_data1,
                                                                                                trip_data2)
            if price1 and price2:
                return ("Two Connections stay in the beginning in {} at {}".format(connection,
                                                                                   self.pricer.flights_provider.get_departure_flight_date(
                                                                                       trip_data2)), price1 + price2,
                        [trip_data1, trip_data2]  )

        return None

    def check_two_connections_stay_in_the_end(self, origin, dest, depart_date, return_date, connection):
        depart_dates = []
        for i in range(4):
            depart_from_dest_date = return_date - timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_dest_date))

        price1, trip_data1 = self.pricer.get_price_round_trip(origin, connection, self._create_str_date(depart_date),
                                                              depart_dates)
        price2, trip_data2 = self.pricer.get_price_round_trip(connection, dest, self._create_str_date(depart_date),
                                                              self._create_str_date(return_date))
        if price1 and price2:
            price1, trip_data1, price2, trip_data2 = self.get_cheapest_flights_that_can_connect(False, trip_data1,
                                                                                                trip_data2)
            if price1 and price2:
                return ("Two Connections stay in the end in {} at {}".format(connection,
                                                                             self.pricer.flights_provider.get_return_flight_date(
                                                                                 trip_data1)), price1 + price2,
                        [trip_data1, trip_data2] )
        return None


    def _create_str_date(self, date):
        return date.strftime("%Y-%m-%d")

    def get_cheapest_flights_that_can_connect(self, is_one_way_flights, trip1, trip2):
        provider = self.pricer.flights_provider
        # return self.pricer.flights_provider.extract_cheapest_price(trip1), trip1['Journeys'][0][0], \
        #        self.pricer.flights_provider.extract_cheapest_price(trip2), trip2['Journeys'][0][0]

        cookie = []
        first_flight, second_flight = self.get_next_flights(trip1, trip2, is_one_way_flights, cookie)
        while first_flight and second_flight:
            if is_one_way_flights:
                if self.flights_can_connect(first_flight["Flights"][-1], second_flight["Flights"][0]):

                    return provider.get_price(first_flight), first_flight, \
                           provider.get_price(second_flight), second_flight
            else:
                connection_arrival, connection_departure = provider.get_dest_flights_in_two_way(first_flight)
                if self.flights_can_connect(connection_arrival, second_flight["Flights"][0]) and \
                   self.flights_can_connect(second_flight["Flights"][-1], connection_departure):

                    return provider.get_price(first_flight), first_flight, \
                           provider.get_price(second_flight), second_flight
                else:
                    print connection_arrival
                    print second_flight["Flights"][0]
                    print second_flight["Flights"][-1]
                    print connection_departure
                    print trip2
                    print trip2


            first_flight, second_flight = self.get_next_flights(trip1, trip2, is_one_way_flights, cookie)



        return None, None, None ,None

    def get_next_flights(self, trip1, trip2, is_one_way_flights, cookie):
        update_second = False
        first_jump_price = second_jump_price = 0
        #for smaller code
        provider = self.pricer.flights_provider

        if not cookie:
            first_index = second_index = first_base_index = second_base_index = 0
            for _ in xrange(4):
                cookie.append(0)
        else:
            first_index = cookie[0]
            second_index = cookie[1]
            first_base_index = cookie[2]
            second_base_index = cookie[3]

        if first_index == constants.MAX_FLIGHTS_PER_TRIP - 1:
            if second_index == constants.MAX_FLIGHTS_PER_TRIP - 1:
                return None, None
            update_second = True

        elif second_index != constants.MAX_FLIGHTS_PER_TRIP - 1:
            first_jump_price = provider.get_price(provider.get_flight(trip1, first_index + 1)) - \
                               provider.get_price(provider.get_flight(trip1, first_base_index))

            second_jump_price = provider.get_price(provider.get_flight(trip2, second_index + 1)) - \
                                provider.get_price(provider.get_flight(trip2, second_base_index))

        if first_jump_price < second_jump_price or not update_second:
            first_index += 1
            second_base_index += 1
            second_index = second_base_index
        else:
            second_index += 1
            first_base_index += 1
            first_index = first_base_index

        cookie[0] = first_index
        cookie[1] = second_index
        cookie[2] = first_base_index
        cookie[3] = second_base_index

        return provider.get_flight(trip1, first_index), provider.get_flight(trip2, second_index)


    def get_cheapest_flight_and_price(self, trip_data):
        sorted_trips = sorted(trip_data['Journeys'], key=lambda trip: trip[0]['Price']['Total']['Amount'])
        try:
            return sorted_trips[0][0]['Price']['Total']['Amount'], sorted_trips[0][0]
        except:
            print "ERROR getting the cheapest flight", trip_data, sorted_trips
            return (None, None)

    def flights_can_connect(self, flight1, flight2):
        if not flight1 or not flight2:
            return False

        #first check that it's the same airport
        #TODO - see how we handle airport changes in the connections
        if (flight1["Destination"] != flight2["Origin"]):
            print "wrong airports {} != {}".format(flight1["Destination"], flight2["Origin"])
            return False

        #then check that there's a 5 hour connection time (#TODO - why 5?)
        arrival_time = parser.parse(flight1["Arrival"])
        deparure_time = parser.parse(flight2["Departure"])
        delta = deparure_time - arrival_time

        if (delta.total_seconds() / 60 / 60 < 5):
            return False

        return True
