'''
Created on May 15, 2014

@author: magenn
'''

import json
import urllib2
import hashlib
import pprint
import copy
import sys
from collections import defaultdict
from threading import Thread

demo_request_json = {
    "SearchRequest":
        {
            "User": "magenheim@gmail.com",
            "Password": hashlib.sha1("killerman").hexdigest(),
            "ResponseType": "json",
            "PassengerTypes": [{"TypeId": 1, "PaxType": "Adult"}],
            "TripSegments": [],
            "Preferences": {"CheckAvailability": "true"},
            "Channels": [{"Id": 1, "Provider": "Amadeus"}],
            "Suppliers": [{
                              "Id": 1,
                              "PointOfSale": "US",
                              "SearchRules": [{"FareType": "All", "Airline": ["All"], "ChannelID": 1}]
                          }]
        }
}

demo_trip = {
    "Id": 1,
    "SegmentPassengers": {"PassengerGroups": [{"Members": [{"Id": 1, "TypeId": 1, "Cabin": "Any"}]}]},
    "Origin": [],
    "Destination": [],
    "DepartureDates": []
}


def build_trip(origin, dest, date, trip_id=1):
    trip = defaultdict(list)
    trip["Id"] = trip_id
    trip["SegmentPassengers"] = {"PassengerGroups": [{"Members": [{"Id": 1, "TypeId": 1, "Cabin": "Any"}]}]}
    trip["Origin"].append(origin)
    trip["Destination"].append(dest)
    trip["DepartureDates"].append({"Date" : date})
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


def get_price(resp):
    return resp['Journeys'][0][0]['Price']['Total']['Amount']



def single_check(origin, dest):
    single_trip = build_trip(origin, dest, "2014-12-18")

    second_trip = build_trip(dest, origin, "2014-12-25")

    trip_data = call_vayant([single_trip])
    if not trip_data:
        return
    go_price = get_price(trip_data)

    trip_data = call_vayant([second_trip])
    if not trip_data:
        return
    ret_price = get_price(trip_data)

    second_trip = build_trip(dest, origin, "2014-12-25", 2)
    trip_data = call_vayant([single_trip, second_trip])
    if not trip_data:
        return
    two_way_price = get_price(trip_data)



    if go_price + ret_price < two_way_price:
        print origin + "->" + dest + "->" + origin + ":"
        print "go", go_price
        print "ret", ret_price
        print "two way", two_way_price
        print "diff", two_way_price - (go_price + ret_price)

    print "END"


if __name__ == "__main__":

    origins = ["TLV", "LON", "NYC", "MAN", "LAX", "WAS", "BKK"]

    for origin in origins:
        for dest in origins:
            if dest != origin:
                t = Thread(target=single_check, args=(origin, dest))
                t.start()
                #single_check(origin, dest)
        #pprint.pprint( resp['Journeys'][0][0]['Price']['Total']['Amount'])

        #pprint.pprint(json.dumps(resp)[0:100])