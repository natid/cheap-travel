from datetime import timedelta

from dateutil import parser
import constants
from flights_data.async_infrastructure.async_response import AsyncResponse, AsyncMultiResponse
from flights_data.async_infrastructure.response_collector import ResponseCollector


class FlightChecker(object):
    def __init__(self, vayant_connector):
        self.pricer = vayant_connector

    def run_test_list(self, origin, dest, depart_date, return_date, connection1, connection2):
        resp_collector = ResponseCollector()
        test_list = self.get_test_list()
        for test in test_list:
            test(origin, dest, depart_date, return_date, connection1, connection2, resp_collector)

        return AsyncMultiResponse(resp_collector)

    def get_test_list(self):
        return (self.check_round_trip,
                self.check_two_one_ways,
                self.check_connection_in_the_beginning,
                self.check_connection_in_the_end,
                self.check_two_connections_stay_in_the_beginning,
                self.check_two_connections_stay_in_the_end)

    def check_round_trip(self, origin, dest, depart_date, return_date, connection1, connection2, resp_collector):
        response = self.pricer.get_price_round_trip(origin, dest, self._create_str_date(depart_date),
                                                              self._create_str_date(return_date))
        def do_after_done(resp):
            price1, trip_data1 = resp['first']
            if price1:
                price1, trip_data1 = self.get_cheapest_flight_and_price(trip_data1)
                return ("Round Trip", price1, [trip_data1])
            else:
                return None

        resp_collector.add_response("round_trip", "first", response, do_after_done)
        

    def check_two_one_ways(self, origin, dest, depart_date, return_date, connection1, connection2, resp_collector):
        response1 = self.pricer.get_price_one_way(origin, dest, self._create_str_date(depart_date))
        response2 = self.pricer.get_price_one_way(dest, origin, self._create_str_date(return_date))

        def do_after_done(resp):
            price1, trip_data1 = resp['first']
            price2, trip_data2 = resp['second']
            if price1 and price2:
                price1, trip_data1 = self.get_cheapest_flight_and_price(trip_data1)
                price2, trip_data2 = self.get_cheapest_flight_and_price(trip_data2)
                return ( "Two one ways", price1 + price2, [trip_data1, trip_data2])
            else:
                return None

        resp_collector.add_response("two_one_ways", "first", response1, do_after_done)
        resp_collector.add_response("two_one_ways", "second", response2, do_after_done)

    def check_two_one_ways_from_different_connections(self, origin, dest, depart_date, return_date, connection1, connection2, resp_collector):

        depart_dates = []
        for i in range(constants.CONNECTION_DAYS):
            depart_from_connection_date = depart_date + timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_connection_date))

        return_dates = []
        for i in range(constants.CONNECTION_DAYS):
            depart_from_dest_date = return_date - timedelta(days=i)
            return_dates.append(self._create_str_date(depart_from_dest_date))

        response1 = self.pricer.get_price_one_way(origin, connection1, self._create_str_date(depart_date))
        response2 = self.pricer.get_price_one_way(connection1, dest, depart_dates)
        response3 = self.pricer.get_price_one_way(dest, connection2, return_dates)
        response4 = self.pricer.get_price_one_way(connection2, origin, self._create_str_date(return_date))


        def do_after_done(resp):
            price1, trip_data1 = resp['first']
            price2, trip_data2 = resp['second']
            price3, trip_data3 = resp['third']
            price4, trip_data4 = resp['forth']

            if price1 and price2 and price3:
                price3, trip_data3 = self.get_cheapest_flight_and_price(trip_data3)
                price1, trip_data1, price2, trip_data2 = self.get_cheapest_flights_that_can_connect(True, trip_data1,
                                                                                                    trip_data2, connection1)
                price3, trip_data3, price4, trip_data4 = self.get_cheapest_flights_that_can_connect(True, trip_data3,
                                                                                                    trip_data4, connection2)
                if price1 and price2 and price3 and price4:
                    return ("4 one way flights in {} and {}".format(connection1,connection2),
                            price1 + price2 + price3 +price4, [trip_data1, trip_data2, trip_data3, trip_data4] )
            return None

        resp_collector.add_response("two_one_ways_from_different_connections", "first", response1, do_after_done)
        resp_collector.add_response("two_one_ways_from_different_connections", "second", response2, do_after_done)
        resp_collector.add_response("two_one_ways_from_different_connections", "third", response3, do_after_done)
        resp_collector.add_response("two_one_ways_from_different_connections", "forth", response4, do_after_done)


    def check_connection_in_the_beginning(self, origin, dest, depart_date, return_date, connection1, connection2, resp_collector):
        depart_dates = []
        for i in range(constants.CONNECTION_DAYS):
            depart_from_connection_date = depart_date + timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_connection_date))

        response1 = self.pricer.get_price_one_way(origin, connection1, self._create_str_date(depart_date))
        response2 = self.pricer.get_price_one_way(connection1, dest, depart_dates)
        response3 = self.pricer.get_price_one_way(dest, origin, self._create_str_date(return_date))

        def do_after_done(resp):
            price1, trip_data1 = resp['first']
            price2, trip_data2 = resp['second']
            price3, trip_data3 = resp['third']
            if price1 and price2 and price3:
                price3, trip_data3 = self.get_cheapest_flight_and_price(trip_data3)
                price1, trip_data1, price2, trip_data2 = self.get_cheapest_flights_that_can_connect(True, trip_data1,
                                                                                                    trip_data2, connection1)
                if price1 and price2:
                    return ("Connection in beginning in {} at {}".format(connection1,
                                                                         self.pricer.flights_provider.get_departure_flight_date(
                                                                             trip_data2)), price1 + price2 + price3,
                            [trip_data1, trip_data2, trip_data3] )
            return None

        resp_collector.add_response("connection_in_the_beginning", "first", response1, do_after_done)
        resp_collector.add_response("connection_in_the_beginning", "second", response2, do_after_done)
        resp_collector.add_response("connection_in_the_beginning", "third", response3, do_after_done)

    def check_connection_in_the_end(self, origin, dest, depart_date, return_date, connection1, connection2, resp_collector):
        depart_dates = []
        for i in range(constants.CONNECTION_DAYS):
            depart_from_dest_date = return_date - timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_dest_date))

        response1 = self.pricer.get_price_one_way(origin, dest, self._create_str_date(depart_date))
        response2 = self.pricer.get_price_one_way(dest, connection1, depart_dates)
        response3 = self.pricer.get_price_one_way(connection1, origin, self._create_str_date(return_date))

        def do_after_done(resp):
            price1, trip_data1 = resp['first']
            price2, trip_data2 = resp['second']
            price3, trip_data3 = resp['third']
            if price1 and price2 and price3:
                price1, trip_data1 = self.get_cheapest_flight_and_price(trip_data1)
                price2, trip_data2, price3, trip_data3 = self.get_cheapest_flights_that_can_connect(True, trip_data2,
                                                                                                    trip_data3, connection1)
                if price2 and price3:
                    return ("Connection in the end in {} at {}".format(connection1,
                                                                       self.pricer.flights_provider.get_departure_flight_date(
                                                                           trip_data2)), price1 + price2 + price3,
                            [trip_data1, trip_data2, trip_data3] )
            return None

        resp_collector.add_response("connection_in_the_end", "first", response1, do_after_done)
        resp_collector.add_response("connection_in_the_end", "second", response2, do_after_done)
        resp_collector.add_response("connection_in_the_end", "third", response3, do_after_done)

    def check_two_connections_stay_in_the_beginning(self, origin, dest, depart_date, return_date, connection1, connection2, resp_collector):
        depart_dates = []
        for i in range(constants.CONNECTION_DAYS):
            depart_from_connection_date = depart_date + timedelta(days=i)
            depart_dates.append(self._create_str_date(depart_from_connection_date))

        response1 = self.pricer.get_price_round_trip(origin, connection1, self._create_str_date(depart_date),
                                                              self._create_str_date(return_date))
        response2 = self.pricer.get_price_round_trip(connection1, dest, depart_dates,
                                                              self._create_str_date(return_date))
        def do_after_done(resp):
            price1, trip_data1 = resp['first']
            price2, trip_data2 = resp['second']
            if price1 and price2:
                price1, trip_data1, price2, trip_data2 = self.get_cheapest_flights_that_can_connect(False, trip_data1,
                                                                                                    trip_data2, connection1)
                if price1 and price2:
                    return ("Two Connections stay in the beginning in {} at {}".format(connection1,
                                                                                       self.pricer.flights_provider.get_departure_flight_date(
                                                                                           trip_data2)), price1 + price2,
                            [trip_data1, trip_data2]  )

            return None

        resp_collector.add_response("two_connections_stay_in_the_beginning", "first", response1, do_after_done)
        resp_collector.add_response("two_connections_stay_in_the_beginning", "second", response2, do_after_done)

    def check_two_connections_stay_in_the_end(self, origin, dest, depart_date, return_date, connection1, connection2, resp_collector):
        return_dates = []
        for i in range(constants.CONNECTION_DAYS):
            depart_from_dest_date = return_date - timedelta(days=i)
            return_dates.append(self._create_str_date(depart_from_dest_date))

        response1 = self.pricer.get_price_round_trip(origin, connection1, self._create_str_date(depart_date),
                                                              self._create_str_date(return_date))
        response2 = self.pricer.get_price_round_trip(connection1, dest, self._create_str_date(depart_date),
                                                              return_dates)
        def do_after_done(resp):
            price1, trip_data1 = resp['first']
            price2, trip_data2 = resp['second']
            if price1 and price2:
                price1, trip_data1, price2, trip_data2 = self.get_cheapest_flights_that_can_connect(False, trip_data1,
                                                                                                    trip_data2, connection1)
                if price1 and price2:
                    return ("Two Connections stay in the end in {} at {}".format(connection1,
                                                                                 self.pricer.flights_provider.get_return_flight_date(
                                                                                     trip_data1)), price1 + price2,
                            [trip_data1, trip_data2] )
            return None

        resp_collector.add_response("two_connections_stay_in_the_end", "first", response1, do_after_done)
        resp_collector.add_response("two_connections_stay_in_the_end", "second", response2, do_after_done)


    def _create_str_date(self, date):
        return date.strftime("%Y-%m-%d")

    def get_cheapest_flights_that_can_connect(self, is_one_way_flights, trip1, trip2, connection):
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
                connection_arrival, connection_departure = provider.get_dest_flights_in_two_way(first_flight, connection)
                if self.flights_can_connect(connection_arrival, second_flight["Flights"][0]) and \
                   self.flights_can_connect(second_flight["Flights"][-1], connection_departure):

                    return provider.get_price(first_flight), first_flight, \
                           provider.get_price(second_flight), second_flight


            first_flight, second_flight = self.get_next_flights(trip1, trip2, is_one_way_flights, cookie)



        return None, None, None ,None

    def get_next_flights(self, trip1, trip2, is_one_way_flights, cookie):
        update_second = False
        first_jump_price = second_jump_price = 0
        #for smaller code
        provider = self.pricer

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
            return False

        #then check that there's a 5 hour connection time (#TODO - why 5?)
        arrival_time = parser.parse(flight1["Arrival"])
        deparure_time = parser.parse(flight2["Departure"])
        delta = deparure_time - arrival_time

        if (delta.total_seconds() / 60 / 60 < 0):
            # print "There is not enough conction time between flights. only {} hours, is_one_way_flights={}".format(delta.total_seconds() / 60 / 60, is_one_way_flights)
            # print "flight1 departure={} , flight1 arrival = {}".format(flight1["Departure"],flight1["Arrival"])
            # print "flight2 departure={} , flight1 arrival = {}".format(flight2["Departure"],flight2["Arrival"])
            return False

        return True
