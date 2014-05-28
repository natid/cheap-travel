#!/usr/bin/python
'''
Created on May 15, 2014

@author: magenn
'''

import json
import urllib2
import hashlib
from collections import defaultdict
import threading
import time
import pprint
import utils

connection=set()

demo_request_json = {
    "SearchRequest":
        {
            "User": "magenheim@gmail.com",
            "Password": hashlib.sha1("killerman").hexdigest(),
            "ResponseType": "json",
            "PassengerTypes": [{"TypeId": 1, "PaxType": "Adult"}],
            "TripSegments": [],
            "Preferences": {"CheckAvailability": "true",}, #"SplitTickets": { "AllowSplitTickets": "true" },},
            "Channels": [{"Id": 1, "Provider": "Amadeus"},
                         {"Id": 2, "Provider": "WorldSpan"},
                         {"Id": 3, "Provider": "Galileo"},
                         {"Id": 4, "Provider": "Sabre"},
                         {"Id": 5, "Provider": "Apollo"},
                         {"Id": 6, "Provider": "DirectConnect"},
                         {"Id": 7, "Provider": "Pyton"}],
            "Suppliers": [{
                              "Id": 1,
                              "PointOfSale": "US",
                              "SearchRules": [{"FareType": "All", "Airline": ["All"], "ChannelID": 1}]
                          }]
        }
}


def build_trip(origin, dest, date, trip_id=1):
    trip = defaultdict(list)
    trip["Id"] = trip_id
    trip["SegmentPassengers"] = {"PassengerGroups": [{"Members": [{"Id": 1, "TypeId": 1, "Cabin": "Any"}]}]}
    trip["Origin"].append(origin)
    trip["Destination"].append(dest)
    trip["DepartureDates"].append({"Date": date})
    return trip


def call_vayant(trip):
    demo_request_json["SearchRequest"]["TripSegments"] = trip

    header = {"Content-Type": "application/JSON "}

    req = urllib2.Request("http://fs-json.demo.vayant.com:7080/", data=json.dumps(demo_request_json), headers=header)

    json_resp = urllib2.urlopen(req)

    resp = json.load(json_resp)

    if resp.has_key('Response') and resp['Response'] == 'Error':
        print "ERROR!!!"
        print resp['Message']
        return None

    return resp


def _extract_cheapest_price(resp):
    return resp['Journeys'][0][0]['Price']['Total']['Amount']

def get_price_round_trip(origin, dest, depart_date, arrive_date):
    first_trip = build_trip(origin, dest, depart_date, 1)
    second_trip = build_trip(dest, origin, arrive_date, 2)
    trip_data = call_vayant([first_trip, second_trip])

    if not trip_data:
        return

    return _extract_cheapest_price(trip_data), trip_data['Journeys'][0][0]

def get_price_one_way(origin, dest, depart_date):
    first_trip = build_trip(origin, dest, depart_date, 1)
    trip_data = call_vayant([first_trip])

    if not trip_data:
        return

    return _extract_cheapest_price(trip_data), trip_data['Journeys'][0][0]

def single_check(origin, dest):
    global connection
    single_trip = build_trip(origin, dest, "2014-12-18")

    second_trip = build_trip(dest, origin, "2014-12-25")

    go_trip_data = call_vayant([single_trip])
    if not go_trip_data:
        return
    go_price = utils.get_price(go_trip_data)

    return_trip_data = call_vayant([second_trip])
    if not return_trip_data:
        return
    ret_price = utils.get_price(return_trip_data)

    second_trip = build_trip(dest, origin, "2014-12-25", 2)
    two_way_trip_data = call_vayant([single_trip, second_trip])
    if not two_way_trip_data:
        return
    two_way_price = utils.get_price(two_way_trip_data)

    if go_price + ret_price  < two_way_price:
        print origin + "->" + dest + "->" + origin + ":"
        utils.print_trip(go_trip_data)
        utils.print_trip(return_trip_data)
        utils.print_trip(two_way_trip_data)

    connection = connection.union(utils.get_connections_list(go_trip_data))

   # print "END"


if __name__ == "__main__":
    origins = ["LON", "AMS", "BER", "ROM", "PAR"]
    dests = ["BKK", "MNL", "HKG"]

    utils.get_connections(origins,dests, single_check)
    print connection


