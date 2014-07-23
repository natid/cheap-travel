from thread_pool import ThreadPool
from flights_data.flight_checks import FlightChecker

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


def get_single_check(origin, dest, depart_date, return_date, flight_checker):

    dict_key = get_dict_key(origin, dest, depart_date, return_date)
    final_prices = flight_checker.pricer.flights_provider.flights_resp_dal.get_results(dict_key)

    if final_prices:
        return final_prices

    area = flight_checker.pricer.flights_provider.flights_resp_dal.get_area_code(origin, dest)
    connections_list = flight_checker.pricer.flights_provider.flights_resp_dal.get_connections_in_area(area)

    pool = ThreadPool(20, "flight_checker", FlightChecker)

    for single_connection in connections_list[0]:
        if origin != dest != single_connection != origin:
            pool.add_task(check_flights, origin, dest, single_connection, depart_date, return_date)

    pool.start()
    pool.wait_completion()

    final_prices = flight_checker.pricer.flights_provider.flights_resp_dal.get_results(dict_key)

    return final_prices
