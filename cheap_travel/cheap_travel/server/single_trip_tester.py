from thread_pool import ThreadPool
from flights_data.flight_checks import FlightChecker

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




def get_single_check(origin, dest, depart_date, return_date):
    final_prices = {}
    flight_checker = FlightChecker()

    area = flight_checker.pricer.flights_provider.flights_resp_dal.get_area_code(origin, dest)
    connections_list = flight_checker.pricer.flights_provider.flights_resp_dal.get_connections_in_area(area)

    pool = ThreadPool(20, "flight_checker", FlightChecker)

    print area
    print connections_list
    for single_connection in connections_list[0]:
        if origin != dest != single_connection != origin:
            pool.add_task(check_flights, origin, dest, single_connection, depart_date, return_date, final_prices)
    pool.start()
    pool.wait_completion()

    return final_prices
