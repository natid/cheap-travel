from datetime import date
from thread_pool import ThreadPool
from flights_data.pricer import Pricer
from flights_data.flight_checks import FlightChecker
import time

def check_flights(origin, dest, connection, depart_date, return_date, results_dict, flight_checker):

    prices = []
    test_list = flight_checker.get_test_list()

    for test in test_list:
        data = test(origin, dest, depart_date, return_date, connection, None)
        if data:
            prices.append(data)

    if prices:
        min_price = min(prices, key=lambda x: x[1])
        dict_key = "%s-%s" % (origin, dest)

        #TODO - we need to make this thread safe
        if results_dict.has_key(dict_key):
            if results_dict[dict_key][1] > min_price[1]:
                results_dict[dict_key] = min_price
        else:
            results_dict[dict_key] = min_price



if __name__ == "__main__":
    start_time = time.time()
    final_prices = {}
    flight_checker = FlightChecker()

    origin = 'SLC'
    dest = 'SOF'

    depart_date = date(2014, 11, 18)
    return_date = date(2014, 12, 26)

    area = flight_checker.pricer.flights_provider.flights_resp_dal.get_area_code(origin, dest)
    connections_list = flight_checker.pricer.flights_provider.flights_resp_dal.get_connections_in_area(area)
    #connections_list = [u'CPH', u'CTU', u'DOH', u'CMB', u'IST', u'CAI', u'KUL', u'DEL', u'CAN', u'MUC', u'PEK', u'FRA', u'SIN', u'BAH', u'AMM', u'KWI', u'BKK', u'MNL', u'PVG', u'SGN', u'AMS', u'HKG', u'BWN', u'SVO', u'TPE', u'ICN', u'HAN', u'AUH', u'ADD', u'LHR', u'HEL', u'ZRH', u'RUH', u'CDG', u'VIE', u'MAN', u'XMN', u'MAA', u'MCT', u'DXB', u'ARN', u'BOM']

    pool = ThreadPool(20, "flight_checker", FlightChecker)

    print area
    print connections_list
    for single_connection in connections_list[0]:
        if origin != dest != single_connection != origin:
            pool.add_task(check_flights, origin, dest, single_connection, depart_date, return_date, final_prices)
    pool.start()
    pool.wait_completion()

    print final_prices
    for cities, price in final_prices.iteritems():
        print "{}, {}, price = {}, flights information is: \n".format(cities, price[0], price[1])
        for flight in price[2]:
            flight_checker.pricer.flights_provider.print_single_flight(flight)


    print "total time it took = {}".format(time.time()-start_time)

