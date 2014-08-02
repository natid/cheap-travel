import json
import urllib2
import hashlib
from collections import defaultdict
import time
import zlib

from cheap_travel.db.flights_resp import FlightsRespDAL


trips_cache = defaultdict()

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


class VayantConnector(object):
    def __init__(self):
        self.flights_resp_dal = FlightsRespDAL()


    def get_flights_info(self, trip):
        resp = None
        key = self._create_cache_key_from_trip(trip)
        #a = time.time()
        cached_resp = self.flights_resp_dal.get(key)
        #print "Query time is {} size is {}".format(time.time() - a, sys.getsizeof
        while self.flights_resp_dal.has_key(key) and cached_resp is None:
            time.sleep(5)
            cached_resp = self.flights_resp_dal.get(key)
        if cached_resp:
            return cached_resp

        try:
            self.flights_resp_dal.set(key, None)

            request_json = demo_request_json.copy()
            request_json["SearchRequest"]["TripSegments"] = trip

            header = {"Content-Type": "application/JSON ", "Accept-encoding": "gzip"}
            req = urllib2.Request("http://fs-json.demo.vayant.com:7080/", data=json.dumps(request_json), headers=header)
            response = urllib2.urlopen(req)
            resp = self._decompress_and_extract_json(response)

            if resp.has_key('Response') and resp['Response'] == 'Error':
                #print "ERROR!!! flight info: {}->{}".format(trip["Origin"][0], trip["Destination"][0]) + resp['Message']
                #print json.dumps(trip)
                self.flights_resp_dal.remove(key)
                return None

            self.flights_resp_dal.set(key, resp)
        finally:
            if not resp:
                self.flights_resp_dal.remove(key)

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
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)

        json_resp = ""

        while True:
            data = response.read(8192)
            if not data: break
            if response.info().get('Content-Encoding') == 'gzip':
                data = decompressor.decompress(data)
            json_resp += data

        return json.loads(json_resp)

    def build_trip(self, origin, dest, dates, trip_id=1):
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

    def print_trip(self, trip, num_flights):
        for flight in trip['Journeys'][0:num_flights]:
            self.print_single_flight(flight[0])

    def print_single_flight(self, flight):
        response = "\n"
        response += flight["Fares"][0]["Origin"] + " -> " + flight["Fares"][0]["Destination"] + ":\n"
        response += "total price = {}".format(flight['Price']['Total']['Amount']) + "\n"
        response += "flights details: "+ "\n"
        for leg in flight["Flights"]:
            response += "\t" + leg["Origin"] + " -> " + leg["Destination"] + ":"+ "\n"
            response += "\t departure: " + leg["Departure"]+ "\n"
            response += "\t arrival: " + leg["Arrival"]+ "\n"
            if self.flights_resp_dal.get_airline(leg["OperatingCarrier"]) is not None:
                response += "\t carrier: " + self.flights_resp_dal.get_airline(leg["OperatingCarrier"])+ "\n"
            else:
                response += "\t carrier: " + leg["OperatingCarrier"]+ "\n"
        return response

    def get_first_flight_from_trip(self, trip_data):
        return trip_data['Journeys'][0][0]

    def get_departure_flight_date(self, trip_response):
        return trip_response['Flights'][0]['Departure'][0:10]

    def get_return_flight_date(self, trip_response):
        return trip_response['Flights'][-1]['Departure'][0:10]

    def extract_cheapest_price(self, resp):
        sorted_response = sorted(resp['Journeys'], key=lambda trip: trip[0]['Price']['Total']['Amount'])
        try:
            return sorted_response[0][0]['Price']['Total']['Amount']
        except:
            print "ERROR getting the price", resp, sorted_response
            return 0

    def get_connections_list(self, trip):
        connections = set()
        for single in trip['Journeys']:
            if len(single[0]["Flights"]) == 2:
                if single[0]["Flights"][0]["Destination"] == single[0]["Flights"][1]["Origin"]:
                    connections.add(single[0]["Flights"][0]["Destination"])
        return connections

    def get_flight(self, trip, index):
        try:
            x = trip['Journeys'][index][0]
            return x
        except:
            return None

    def get_price(self, flight):
        if flight:
            return flight['Price']['Total']['Amount']
        return 99999

    def get_dest_flights_in_two_way(self, trip, connection):
        for i in xrange(len(trip['Flights'])):
            if trip['Flights'][i]['Destination'] == connection:
                return trip['Flights'][i], trip['Flights'][i + 1]

        return None, None

