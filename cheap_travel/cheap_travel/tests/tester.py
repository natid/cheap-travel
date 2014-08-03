from datetime import date, timedelta
from flights_data.flight_checker import FlightChecker
from thread_pool import ThreadPool
from flights_data.pricer import Pricer

def check_flights(origin, dest, connection, depart_date, return_date, results_dict, flight_checker):
    prices = []
    test_list = flight_checker.get_test_list()

    for test in test_list:
        data = test(origin, dest, depart_date, return_date, connection, None)
        if data:
            prices.append(data)

    if prices:
        min_price = min(prices, key=lambda x: x[1])

        if "Round Trip" not in min_price[0]:
            dict_key = "%s-%s, %s, %s" % (origin, dest, depart_date, return_date)
            flight_checker.pricer.flights_provider.flights_resp_dal.insert_results_to_db(dict_key, prices)

        #TODO - we need to make this thread safe
        # if results_dict.has_key(dict_key):
        #     if results_dict[dict_key][1] > min_price[1]:
        #         results_dict[dict_key] = min_price
        # else:
        #     results_dict[dict_key] = min_price


final_prices = {}

origin_list = ['LON', 'BER', 'AMS', 'ROM', 'PAR', 'ZRH']
dest_list = ['MNL', 'BKK', 'HKG', 'BJS']

connections_list = [u'CPH', u'CTU', u'DOH', u'CMB', u'IST', u'CAI', u'KUL', u'DEL', u'CAN', u'MUC', u'PEK', u'FRA', u'SIN', u'BAH', u'AMM', u'KWI', u'BKK', u'MNL', u'PVG', u'SGN', u'AMS', u'HKG', u'BWN', u'SVO', u'TPE', u'ICN', u'HAN', u'AUH', u'ADD', u'LHR', u'HEL', u'ZRH', u'RUH', u'CDG', u'VIE', u'MAN', u'XMN', u'MAA', u'MCT', u'DXB', u'ARN', u'BOM']
#connections_list = get_all_connections(origin_list, dest_list)

depart_dates = [date(2014, 11, 02), date(2014, 9, 15), date(2015, 01, 01), date(2014, 8, 02), date(2014, 07, 25)]
return_dates = [depart_date  + timedelta(days=21) for depart_date in depart_dates]
return_dates += [depart_date  + timedelta(days=7) for depart_date in depart_dates]
return_dates += [depart_date  + timedelta(days=80) for depart_date in depart_dates]

if __name__ == "__main__":

    pool = ThreadPool(20, "flight_checker", FlightChecker)

    for dest in dest_list:
        for single_connection in connections_list:
            for origin in origin_list:
                for depart_date in depart_dates:
                    for return_date in return_dates:
                        if depart_date < return_date :
                            if origin != dest != single_connection != origin:
                                pool.add_task(check_flights, origin, dest, single_connection, depart_date, return_date,
                                              final_prices)
    print "Number of tasks", pool.task_number
    pool.start()
    print "Waiting for completion"
    pool.wait_completion()

    print final_prices
    print len(final_prices)
    for cities, price in final_prices.iteritems():
        if True:#"Round Trip" not in price[0]:
            print "{}, {}, price = {}, flights information is: \n".format(cities, price[0], price[1])
            for flight in price[2]:
                Pricer("Vayant").flights_provider.print_single_flight(flight)



