from thread_pool import ThreadPool
from flights_data.flight_checks import FlightChecker
from flights_data.connection_checker import ConnectionChecker
from flights_data.vayant import VayantConnector
from datetime import datetime

#pool = ThreadPool(20, "flight_checker", FlightChecker)

#pool.start()

def check_flights(origin, dest, connection, depart_date, return_date, flight_checker):

    prices = []
    test_list = flight_checker.get_test_list()

    for test in test_list:
        data = test(origin, dest, depart_date, return_date, connection, None)
        if data:
            prices.append(data)

    if prices:
        dict_key = get_dict_key(origin, dest, depart_date, return_date)
        flight_checker.pricer.flights_provider.flights_resp_dal.insert_results_to_db(dict_key, prices)


def get_dict_key(origin, dest, depart_date, return_date):
    return "%s-%s, %s, %s" % (origin, dest, depart_date, return_date)

def get_cheapest_flight(final_prices):
    found = False
    if final_prices:
        for flight in final_prices:
            if "Round Trip" in flight["type"]:
                round_trip_price = cheapest_trip_price = flight["price"]
                cheapest_flight = flight["flight"]
                cheapest_type = flight["type"]
                found  = True
                break
        if not found:
            print "couldn't find round trip"
            return None, None, None, None


        for flight in final_prices:
            if flight["price"] < cheapest_trip_price:
                cheapest_type = flight["type"]
                cheapest_trip_price = flight["price"]
                cheapest_flight = flight["flight"]

        return round_trip_price, cheapest_trip_price, cheapest_flight, cheapest_type
    else:
        return None, None, None, None

def get_single_check(origin, dest, depart_date, return_date, flight_checker):

    dict_key = get_dict_key(origin, dest, depart_date, return_date)
    final_prices = flight_checker.pricer.flights_provider.flights_resp_dal.get_results(dict_key)

    if final_prices:
        return final_prices

    area = flight_checker.pricer.flights_provider.flights_resp_dal.get_area_code(origin, dest)
    connections_list = flight_checker.pricer.flights_provider.flights_resp_dal.get_connections_in_area(area)

    if len(connections_list) == 0:
        print "couldn't get connection list"
        return None


    for single_connection in connections_list[0]:
        if origin != dest != single_connection != origin:
            pass#pool.add_task(check_flights, origin, dest, single_connection, depart_date, return_date)

    #pool.wait_completion()

    final_prices = flight_checker.pricer.flights_provider.flights_resp_dal.get_results(dict_key)

    return final_prices

def new_single_check(origin, dest, depart_date, return_date, vayant_connector):
    connection_checker = ConnectionChecker(vayant_connector)
    return connection_checker.run_connection_check(origin, dest, depart_date, return_date)

# from flights_data.flight_checks import FlightChecker
# import time
# from pprint import pprint
# pprint(FlightChecker(VayantConnector()).check_round_trip("TLV", "BKK", datetime(2014, 8, 12), datetime(2014, 8, 23), None, None, None))
# time.sleep(3000)