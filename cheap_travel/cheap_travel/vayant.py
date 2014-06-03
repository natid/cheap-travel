import json
import urllib2
import hashlib
from collections import defaultdict
import time
import utils
import zlib
import bl

trips_cache = defaultdict()

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


def build_trip(origin, dest, dates, trip_id=1):
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

def create_cache_key_from_trip(trip):
    key = ""
    for single_trip in trip:
        key += single_trip["Origin"][0] + "-"
        key += single_trip["Destination"][0] + "-"
        for date in single_trip["DepartureDates"]:
            key += date["Date"] + "-"
        key += ":"
    return key


def decompress_and_extract_json(response):
    decompressor = zlib.decompressobj(16+zlib.MAX_WBITS)

    json_resp = ""

    while True:
        data = response.read(8192)
        if not data: break
        if response.info().get('Content-Encoding') == 'gzip':
            data = decompressor.decompress(data)
        json_resp += data

    return json.loads(json_resp)


def call_vayant(trip):
    key = create_cache_key_from_trip(trip)

    while key in trips_cache and not trips_cache[key]:
        time.sleep(5)
    if key in trips_cache:
        return trips_cache[key]

    trips_cache[key]=None

    request_json = demo_request_json.copy()
    request_json["SearchRequest"]["TripSegments"] = trip

    header = {"Content-Type": "application/JSON ", "Accept-encoding": "gzip"}

    req = urllib2.Request("http://fs-json.demo.vayant.com:7080/", data=json.dumps(request_json), headers=header)

    response = urllib2.urlopen(req)

    resp = decompress_and_extract_json(response)

    if resp.has_key('Response') and resp['Response'] == 'Error':
        print "ERROR!!!"+ resp['Message']
        print trip
        trips_cache.remove(key)
        return None

    trips_cache[key] = resp

    return resp


if __name__ == "__main__":
    origins = ["LON", "AMS", "BER", "ROM", "PAR"]
    dests = ["BKK", "MNL", "HKG"]

    start = time.time()
    connection = utils.get_all_connections(origins, dests, bl.get_connections)
    print connection



