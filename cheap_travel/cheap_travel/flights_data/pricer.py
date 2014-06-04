__author__ = 'magenn'

import Queue
import threading
import time
from collections import defaultdict

import utils
from vayant import VayantConnector


class Pricer(object):

    def __init__(self):
        self.vayant_connector = VayantConnector()

    def get_price_round_trip(self, origin, dest, depart_dates, arrive_dates):
        first_trip = self._build_trip(origin, dest, depart_dates, 1)
        second_trip = self._build_trip(dest, origin, arrive_dates, 2)
        trip_data = self.vayant_connector.call_vayant([first_trip, second_trip])

        if not trip_data:
            return (None, None)

        return utils.extract_cheapest_price(trip_data), trip_data

    def get_price_one_way(self, origin, dest, depart_dates, get_full_response = False):
        first_trip = self._build_trip(origin, dest, depart_dates, 1)
        trip_data = self.vayant_connector.call_vayant([first_trip])

        if not trip_data:
            return (None, None)

        return utils.extract_cheapest_price(trip_data), trip_data

    def _build_trip(self, origin, dest, dates, trip_id=1):
        trip = defaultdict(list)
        trip["Id"] = trip_id
        trip["SegmentPassengers"] = {"PassengerGroups": [{"Members": [{"Id": 1, "TypeId": 1, "Cabin": "Any"}]}]}
        trip["Origin"].append(str(origin))
        trip["Destination"].append(str(dest))

        if type(dates) is str:
            trip["DepartureDates"].append({"Date": dates})
        elif type(dates) is list:
            for date in dates:
                trip["DepartureDates"].append({"Date": date})
        else:
            assert False, "wrong dates type"

        return trip


def get_connections(origin, dest, queue):
    pricer = Pricer()
    go_trip_data = pricer.get_price_one_way(origin, dest, "2014-12-18", True)[1]

    queue.put(utils.get_connections_list(go_trip_data))

def get_all_connections(origins, dests):
    connections=set()
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
        connections.add(item)

    return connections
