from vayant import get_price
from datetime import date, timedelta
from threading import Thread


def _create_str_date(date):
    return date.strftime("%Y-%m-%d")

def print_flight(origin, connection, dest, depart_date, arrive_date, price):
    print "{0} -> {1} from {2} to {3}".format(origin, connection, depart_date, arrive_date)
    print "{0} -> {1} from {2} to {3}".format(connection, dest, depart_date, arrive_date)
    print "same date", price


def check_flights(origin, dest, connection):
    global final_prices
    prices = []

    for i in range(4):

        depart_from_connection_date = depart_date + timedelta(days=i)

        price = get_price(origin, connection, _create_str_date(depart_date), _create_str_date(arrive_date)) + \
                 get_price(connection, dest, _create_str_date(depart_from_connection_date), _create_str_date(arrive_date))

        prices.append((price, connection, depart_from_connection_date))
        print_flight(origin, connection, dest, depart_date, arrive_date, price)

    min_price = min(prices, key=lambda x: x[0])
    dict_key = "%s-%s" % (origin, dest)

    if final_prices.has_key(dict_key):
        if final_prices[dict_key][0] > min_price[0]:
            final_prices[dict_key] = min_price
    else:
        final_prices[dict_key] = min_price
    """
    print "="*30
    print "MIN from %s to %s via %s is %s" % (origin, dest, connection, min_price[0])
    print "depart from connection in", min_price[1]
    print "="*30
    """

threads = []

#connections_list = ['IST', 'VIE', 'CAN', 'CAI', 'AUH', 'DOH', 'SIN', 'KUL']
connections_list = ['IST']
final_prices = {}

origin_list = ['AMS']
dest_list = ['MNL', 'BKK', 'HKG']

depart_date = date(2014, 11, 02)
arrive_date = depart_date + timedelta(days=21)

for origin in origin_list:
    for dest in dest_list:
        for connection in connections_list:
            if origin != dest != connection:
                t = Thread(target=check_flights, args=(origin, dest, connection))
                t.start()
                threads.append(t)

for t in threads:
    t.join()

print final_prices



