__author__ = 'magenn'

import utils
import vayant
import Queue
import threading
import time

def get_price_round_trip(origin, dest, depart_dates, arrive_dates, get_full_response = False):
    first_trip = vayant.build_trip(origin, dest, depart_dates, 1)
    second_trip = vayant.build_trip(dest, origin, arrive_dates, 2)
    trip_data = vayant.call_vayant([first_trip, second_trip])

    if not trip_data:
        return (None, None)

    trip_to_return = trip_data if get_full_response else trip_data['Journeys'][0][0]
    return utils._extract_cheapest_price(trip_data), trip_to_return

def get_price_one_way(origin, dest, depart_dates, get_full_response = False):
    first_trip = vayant.build_trip(origin, dest, depart_dates, 1)
    trip_data = vayant.call_vayant([first_trip])

    if not trip_data:
        return (None, None)

    trip_to_return = trip_data if get_full_response else trip_data['Journeys'][0][0]
    return utils._extract_cheapest_price(trip_data), trip_to_return

def get_connections(origin, dest, queue):
    go_trip_data = get_price_one_way(origin, dest, "2014-12-18", True)[1]

    queue.put(utils.get_connections_list(go_trip_data))

def get_all_connections(origins, dests):
    connections=set()
    queue = Queue.Queue()
    threads = []

    for origin in origins:
         for dest in dests:
            if dest != origin:
                while threading.activeCount() > 1:
                    time.sleep(5)
                t = threading.Thread(target=get_connections, args=(str(origin).upper(), str(dest).upper(), queue))
                t.start()
                threads.append(t)

    for t in threads:
        t.join()

    for item in queue.get():
        connections.add(item)

    return connections
