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

def get_cheapest_flight(final_prices):
    if final_prices:
        assert("Round Trip" in final_prices[0][0][0])
        round_trip_price = cheapest_trip_price = final_prices[0][0][1]
        cheapest_flight = final_prices[0][0][2]
        cheapest_type = final_prices[0][0][0]
        for options in final_prices:
            for price in options:
                if price[1] < cheapest_trip_price:
                    cheapest_type = price[0]
                    cheapest_trip_price = price[1]
                    cheapest_flight = price[2]

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

    pool = ThreadPool(20, "flight_checker", FlightChecker)

    for single_connection in connections_list[0]:
        if origin != dest != single_connection != origin:
            pool.add_task(check_flights, origin, dest, single_connection, depart_date, return_date)

    pool.start()
    pool.wait_completion()

    final_prices = flight_checker.pricer.flights_provider.flights_resp_dal.get_results(dict_key)

    return final_prices
