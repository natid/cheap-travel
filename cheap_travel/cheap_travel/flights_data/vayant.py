import json
import urllib2
import hashlib
from collections import defaultdict
import time
import zlib
import pricer
import sys
from db.flights_resp import FlightsRespDAL


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


class VayantConnector(object):

    def __init__(self):
        self.flights_resp_dal = FlightsRespDAL()


    def call_vayant(self, trip):
        key = self._create_cache_key_from_trip(trip)

        a = time.time()
        cached_resp = self.flights_resp_dal.get(key)
        while self.flights_resp_dal.has_key(key) and cached_resp is None:
            time.sleep(5)
            cached_resp = self.flights_resp_dal.get(key)
        if cached_resp:
            print len(cached_resp["Journeys"])
            return cached_resp

        self.flights_resp_dal.set(key, None)

        request_json = demo_request_json.copy()
        request_json["SearchRequest"]["TripSegments"] = trip

        header = {"Content-Type": "application/JSON ", "Accept-encoding": "gzip"}

        req = urllib2.Request("http://fs-json.demo.vayant.com:7080/", data=json.dumps(request_json), headers=header)

        response = urllib2.urlopen(req)

        resp = self._decompress_and_extract_json(response)

        if resp.has_key('Response') and resp['Response'] == 'Error':
            print "ERROR!!! "+ resp['Message']
            print json.dumps(trip)
            self.flights_resp_dal.remove(key)
            return None

        self.flights_resp_dal.set(key, resp)
        return resp

    def _create_cache_key_from_trip(self, trip):
        key = ""
        for single_trip in trip:
            key += single_trip["Origin"][0] + "-"
            key += single_trip["Destination"][0] + "-"
            for date in single_trip["DepartureDates"]:
                key += date["Date"] + "-"
            key += ":"
        return key


    def _decompress_and_extract_json(self, response):
        decompressor = zlib.decompressobj(16+zlib.MAX_WBITS)

        json_resp = ""

        while True:
            data = response.read(8192)
            if not data: break
            if response.info().get('Content-Encoding') == 'gzip':
                data = decompressor.decompress(data)
            json_resp += data

        return json.loads(json_resp)


if __name__ == "__main__":
    #origins = ["LON", "AMS", "BER", "ROM", "PAR"]

    #dests = ["BKK", "MNL", "HKG"]

    origins = ["LON"]
    dests = ["BKK"]
    start = time.time()
    connection = pricer.get_all_connections(origins, dests)
    print connection



