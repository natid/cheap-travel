import threading
from vayant import get_price_round_trip, get_price_one_way
from datetime import date, timedelta
from threading import Thread
import time
import utils

def _create_str_date(date):
    return date.strftime("%Y-%m-%d")

def print_flight(origin, connection, dest, depart_date, arrive_date, price, flight_type):
    print "{0} -> {1} from {2} to {3}".format(origin, connection, depart_date, arrive_date)
    print "{0} -> {1} from {2} to {3}".format(connection, dest, depart_date, arrive_date)



def check_flights(origin, dest, connection):
    global final_prices
    prices = []

    # round trip:
    price, round_trip_data = get_price_round_trip(origin, dest, _create_str_date(depart_date), _create_str_date(arrive_date))
    data = ("Round Trip", price, [round_trip_data])
    prices.append(data)

    # two one ways
    price1, trip_data1 = get_price_one_way(origin, dest, _create_str_date(depart_date))
    price2, trip_data2 = get_price_one_way(dest, origin, _create_str_date(arrive_date))
    data = ( "Two one ways",price1+price2,[trip_data1, trip_data2])
    prices.append(data)

    # connection in the beginning of the trip
    for i in range(4):

        depart_from_connection_date = depart_date + timedelta(days=i)

        price1, trip_data1 = get_price_one_way(origin, connection, _create_str_date(depart_date))
        price2, trip_data2 = get_price_one_way(connection, dest, _create_str_date(depart_from_connection_date))
        price3, trip_data3 = get_price_one_way(connection, dest, _create_str_date(arrive_date))


        data = ("Connection in beginning in {} at {}".format(connection, depart_from_connection_date), price1 + price2 + price3, [trip_data1, trip_data2, trip_data3] )
        prices.append(data)

    # connection in the end of the trip
    for i in range(4):

        depart_from_dest_date = arrive_date - timedelta(days=i)

        price1, trip_data1 = get_price_one_way(origin, dest, _create_str_date(depart_date))
        price2, trip_data2 = get_price_one_way(dest, connection , _create_str_date(depart_from_dest_date))
        price3, trip_data3 = get_price_one_way(connection, origin, _create_str_date(arrive_date))

        data = ("Connection in the end in {} at {}".format(connection, depart_from_dest_date), price1 + price2 + price3, [trip_data1, trip_data2, trip_data3] )
        prices.append(data)

    # Two Connections stay in the beginning
    for i in range(4):

        depart_from_connection_date = depart_date + timedelta(days=i)

        price1, trip_data1 = get_price_round_trip(origin, connection, _create_str_date(depart_date), _create_str_date(arrive_date))
        price2, trip_data2 = get_price_round_trip(connection, dest, _create_str_date(depart_from_connection_date), _create_str_date(arrive_date))

        data = ("Two Connections stay in the beginning in {} at {}".format(connection, depart_from_connection_date), price1 + price2, [trip_data1, trip_data2]  )
        prices.append(data)

    # Two Connections stay in the end
    for i in range(4):

        depart_from_dest_date = arrive_date - timedelta(days=i)

        price1, trip_data1 = get_price_round_trip(origin, connection, _create_str_date(depart_date), _create_str_date(depart_from_dest_date))
        price2, trip_data2 = get_price_round_trip(connection, dest, _create_str_date(depart_date), _create_str_date(arrive_date))

        data = ("Two Connections stay in the end in {} at {}".format(connection, depart_from_connection_date), price1 + price2,[trip_data1, trip_data2] )
        prices.append(data)

    min_price = min(prices, key=lambda x: x[1])
    dict_key = "%s-%s" % (origin, dest)

    if final_prices.has_key(dict_key):
        if final_prices[dict_key][1] > min_price[1]:
            final_prices[dict_key] = min_price
    else:
        final_prices[dict_key] = min_price
    """
    print "="*30
    print "MIN from %s to %s via %s is %s" % (origin, dest, connection, min_price[0])
    print "depart from connection in", min_price[1]
    print "="*30
    """

def check_for_origins(origin_list, dest, connection):
    for origin in origin_list:
        if origin != dest != connection:
            check_flights(origin, dest, connection)

threads = []

#connections_list = ['IST', 'VIE', 'CAN', 'CAI', 'AUH', 'DOH', 'SIN', 'KUL']
connections_list = [u'CPH', u'CTU', u'DOH', u'CMB', u'IST', u'CAI', u'KUL', u'DEL', u'CAN', u'MUC', u'PEK', u'FRA', u'SIN', u'BAH', u'AMM', u'KWI', u'BKK', u'MNL', u'PVG', u'SGN', u'AMS', u'HKG', u'BWN', u'SVO', u'TPE', u'ICN', u'HAN', u'AUH', u'ADD', u'LHR', u'HEL', u'ZRH', u'RUH', u'CDG', u'VIE', u'MAN', u'XMN', u'MAA', u'MCT', u'DXB', u'ARN', u'BOM']
final_prices = {}

origin_list = ['LON', 'BER', 'AMS', 'ROM', 'PAR', 'ZRH']
dest_list = ['MNL', 'BKK', 'HKG', 'BJS']

depart_date = date(2014, 11, 02)
arrive_date = depart_date + timedelta(days=21)


for dest in dest_list:
    for connection in connections_list:

        while threading.activeCount() > 20:
            time.sleep(5)
        t = threading.Thread(target=check_for_origins,  args=(origin_list, dest, connection))
        t.start()

while threading.activeCount() > 1:
    time.sleep(10)

#         t = Thread(target=check_for_origins, args=(origin_list, dest, connection))
#         t.start()
#         threads.append(t)
#
# for t in threads:
#     t.join()

for _,price in final_prices.iteritems():
    print "{}, price = {}, flights information is: \n".format(price[0], price[1])
    for flight in price[2]:
        utils.print_single_flight(flight)



