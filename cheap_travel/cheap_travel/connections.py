import threading
from datetime import date, timedelta
import time
from flight_checks import FlightChecker
from utils import ThreadPool
import utils
import flight_checks

final_prices = {}

def check_flights(origin, dest, connection, depart_date, return_date, flight_checker):
    global final_prices
    prices = []
    test_list = (flight_checker.check_round_trip,
                 flight_checker.check_two_one_ways,
                 flight_checker.check_connection_in_the_beginning,
                 flight_checker.check_connection_in_the_end,
                 flight_checker.check_two_connections_stay_in_the_beginning,
                 flight_checker.check_two_connections_stay_in_the_end)


    i=1
    for test in test_list:
        a = time.time()
        data = test(origin, dest, depart_date, return_date, connection)
        #print "WOW ", time.time() - a, i
        if data:
            prices.append(data)
        i+=1


    if prices:
        min_price = min(prices, key=lambda x: x[1])
        dict_key = "%s-%s" % (origin, dest)

        if final_prices.has_key(dict_key):
            if final_prices[dict_key][1] > min_price[1]:
                final_prices[dict_key] = min_price
        else:
            final_prices[dict_key] = min_price

def check_for_origins(origin_list, dest, connection, depart_date, return_date):
    for origin in origin_list:
        if origin != dest != connection != origin:
            check_flights(origin, dest, connection, depart_date, return_date)

if __name__ == "__main__":
    threads = []

    connections_list = [u'CPH', u'CTU', u'DOH', u'CMB', u'IST', u'CAI', u'KUL', u'DEL', u'CAN', u'MUC', u'PEK', u'FRA', u'SIN', u'BAH', u'AMM', u'KWI', u'BKK', u'MNL', u'PVG', u'SGN', u'AMS', u'HKG', u'BWN', u'SVO', u'TPE', u'ICN', u'HAN', u'AUH', u'ADD', u'LHR', u'HEL', u'ZRH', u'RUH', u'CDG', u'VIE', u'MAN', u'XMN', u'MAA', u'MCT', u'DXB', u'ARN', u'BOM']

    origin_list = ['LON', 'BER', 'AMS', 'ROM', 'PAR', 'ZRH']
    dest_list = ['MNL', 'BKK', 'HKG', 'BJS']

    depart_date = date(2014, 11, 02)
    return_date = depart_date + timedelta(days=21)

    progress = 0
    total_options = len(dest_list) * len(connections_list)
    pool = ThreadPool(20, "flight_checker", FlightChecker)

    for dest in dest_list:
        for single_connection in connections_list:
            for origin in origin_list:
                if origin != dest != single_connection != origin:

                    pool.add_task(check_flights, origin, dest, single_connection, depart_date, return_date)

    """
            while threading.activeCount() > 80:
                time.sleep(5)
            if((progress*100/total_options) != (((progress+1)*100)/total_options)):
                print "{} percent done".format(progress*100/total_options)
            progress+=1
            t = threading.Thread(target=check_for_origins,  args=(origin_list, dest, single_connection, depart_date, return_date))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
    """


    print "Number of tasks", pool.task_number
    pool.start()
    print "Waiting for completion"
    pool.wait_completion()

    for cities, price in final_prices.iteritems():
        if "Round Trip" not in cities:
            print "{}, {}, price = {}, flights information is: \n".format(cities, price[0], price[1])
            for flight in price[2]:
                utils.print_single_flight(flight)



