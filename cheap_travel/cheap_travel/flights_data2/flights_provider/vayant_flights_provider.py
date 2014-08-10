import hashlib
import json
from flights_data2.flights_provider.flights_provider import BaseFlightsProvider
import urllib2
from collections import defaultdict
import zlib
from constants import DATE_FORMAT
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

    def call_provider(self, request):
        header = {"Content-Type": "application/JSON ", "Accept-encoding": "gzip"}
        req = urllib2.Request("http://fs-json.demo.vayant.com:7080/", data=json.dumps(request), headers=header)
        response = urllib2.urlopen(req)
        resp = self._decompress_and_extract_json(response)
        if resp.has_key('Response') and resp['Response'] == 'Error':
            print resp
            return None

        return resp

    def _decompress_and_extract_json(self, response):
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)

        json_resp = ""

        while True:
            data = response.read(8192)
            if not data: break
            if response.info().get('Content-Encoding') == 'gzip':
                data = decompressor.decompress(data)
            json_resp += data

        return json.loads(json_resp)

    def build_trip_request(self, trip_data):
        request_json = demo_request_json.copy()
        trip = list()

        trip.append(self._build_trip(trip_data.origin, trip_data.dest, [x.strftime(DATE_FORMAT) for x in trip_data.depart_dates], 1))
        if hasattr(trip_data,"return_dates") and trip_data.return_dates:
            trip.append(self._build_trip(trip_data.dest, trip_data.origin, [x.strftime(DATE_FORMAT) for x in trip_data.return_dates], 2))

        request_json["SearchRequest"]["TripSegments"] = trip

        return request_json

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
            print type(dates)
            assert False, "wrong dates type"

        return trip

    def convert_provider_response(self, flight_data):
        if flight_data.has_key('Response') and flight_data['Response'] == 'Error':
            return None

        trips = []
        for single_vayant_response in flight_data["Journeys"]:
            trip = dict()
            trip["price"] = single_vayant_response[0]["Price"]["Total"]["Amount"]

            trip["legs"] = []

            for single_leg in single_vayant_response[0]["Flights"]:
                leg = dict()
                leg["origin"] = single_leg["Origin"]
                leg["dest"] = single_leg["Destination"]
                leg["carrier"] = single_leg["OperatingCarrier"]
                leg["flight_number"] = single_leg["FlightNumber"]
                leg["departure"] = single_leg["Departure"]
                leg["arrival"] = single_leg["Arrival"]

                trip["legs"].append(leg)

            trips.append(trip)
        return trips