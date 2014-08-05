import hashlib
import json
from flights_data2.flights_provider.flights_provider import BaseFlightsProvider
import urllib2


demo_request_json = {
    "SearchRequest":
        {
            "User": "magenheim@gmail.com",
            "Password": hashlib.sha1("killerman").hexdigest(),
            "ResponseType": "json",
            "PassengerTypes": [{"TypeId": 1, "PaxType": "Adult"}],
            "TripSegments": [],
            "Preferences": {"CheckAvailability": "true", },  #"SplitTickets": { "AllowSplitTickets": "true" },},
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


class VayantFlightsProvider(BaseFlightsProvider):

    def call_provider(self, trip):
        request_json = demo_request_json.copy()
        request_json["SearchRequest"]["TripSegments"] = trip

        header = {"Content-Type": "application/JSON ", "Accept-encoding": "gzip"}
        req = urllib2.Request("http://fs-json.demo.vayant.com:7080/", data=json.dumps(request_json), headers=header)
        response = urllib2.urlopen(req)
        resp = self._decompress_and_extract_json(response)

        if resp.has_key('Response') and resp['Response'] == 'Error':
            #print "ERROR!!! flight info: {}->{}".format(trip["Origin"][0], trip["Destination"][0]) + resp['Message']
            #print json.dumps(trip)
            return None

        return resp

    def build_trip(self, trip):
        pass