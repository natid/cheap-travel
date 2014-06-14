import Queue
import threading
import time
from datetime import date, timedelta
from flights_data.flight_checks import FlightChecker
from thread_pool import ThreadPool
from flights_data.pricer import Pricer


def get_connections(origin, dest, queue):
    pricer = Pricer("Vayant")

    go_trip_data = pricer.get_price_one_way(origin, dest, "2014-12-18", True)[1]
    queue.put(pricer.flights_provider.get_connections_list(go_trip_data))


def get_all_connections(origins, dests):
    connections = set()
    queue = Queue.Queue()
    threads = []

    for origin in origins:
        for dest in dests:
            if dest != origin:
                while threading.activeCount() > 20:
                    time.sleep(5)
                t = threading.Thread(target=get_connections, args=(str(origin).upper(), str(dest).upper(), queue))
                t.start()
                threads.append(t)


    for t in threads:
        t.join()



    for item in queue.get():
        print "test"
        connections.add(item)

    print "nir "
    print type(queue.get())
    print connections

    return connections


def check_flights(origin, dest, connection, depart_date, return_date, results_dict, flight_checker):
    global final_prices
    prices = []
    test_list = (flight_checker.check_round_trip,
                 flight_checker.check_two_one_ways,
                 flight_checker.check_connection_in_the_beginning,
                 flight_checker.check_connection_in_the_end,
                 flight_checker.check_two_connections_stay_in_the_beginning,
                 flight_checker.check_two_connections_stay_in_the_end)

    for test in test_list:
        data = test(origin, dest, depart_date, return_date, connection)
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

    final_prices = {}

    origin_list = ['LON', 'BER', 'AMS', 'ROM', 'PAR', 'ZRH']
    dest_list = ['MNL', 'BKK', 'HKG', 'BJS']

    connections_list = [u'CPH', u'CTU', u'DOH', u'CMB', u'IST', u'CAI', u'KUL', u'DEL', u'CAN', u'MUC', u'PEK', u'FRA', u'SIN', u'BAH', u'AMM', u'KWI', u'BKK', u'MNL', u'PVG', u'SGN', u'AMS', u'HKG', u'BWN', u'SVO', u'TPE', u'ICN', u'HAN', u'AUH', u'ADD', u'LHR', u'HEL', u'ZRH', u'RUH', u'CDG', u'VIE', u'MAN', u'XMN', u'MAA', u'MCT', u'DXB', u'ARN', u'BOM']
    #connections_list = get_all_connections(origin_list, dest_list)

    depart_date = date(2014, 11, 02)
    return_date = depart_date + timedelta(days=21)

    pool = ThreadPool(20, "flight_checker", FlightChecker)

    for dest in dest_list:
        for single_connection in connections_list:
            for origin in origin_list:
                if origin != dest != single_connection != origin:
                    pool.add_task(check_flights, origin, dest, single_connection, depart_date, return_date,
                                  final_prices)
    print "Number of tasks", pool.task_number
    pool.start()
    print "Waiting for completion"
    pool.wait_completion()

    for cities, price in final_prices.iteritems():
        if "Round Trip" not in price[0]:
            print "{}, {}, price = {}, flights information is: \n".format(cities, price[0], price[1])
            for flight in price[2]:
                Pricer("Vayant").flights_provider.print_single_flight(flight)



