import json
import urllib2
import hashlib
from collections import defaultdict
import time
import zlib

from cheap_travel.db.flights_resp import FlightsRespDAL
from thread_pool import ThreadPool
from async_infrastructure.async_response import AsyncResponse

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
        self.pool = ThreadPool(30)
        self.pool.start()


    def get_flight_price_async(self, trip):
        response = AsyncResponse(self.do_after_done)
        self.pool.add_task(self.calculate_flight_info, trip, response)
        return response

    def get_flight_from_cache(self, key):

        cached_resp = self.flights_resp_dal.get(key)
        while self.flights_resp_dal.has_key(key) and cached_resp is None:
            time.sleep(5)
            cached_resp = self.flights_resp_dal.get(key)
        return cached_resp

    def calculate_flight_info(self, trip, response):
        resp = self.get_flights_info(trip)
        response.set_response_value(resp)

    def get_flights_info(self, trip):
        resp = None

        key = self._create_cache_key_from_trip(trip)
        cached_resp = self.get_flight_from_cache(key)
        if cached_resp:
            return cached_resp

        try:
            self.flights_resp_dal.set(key, None)

            request_json = self.build_trip_request(trip_data)

            header = {"Content-Type": "application/JSON ", "Accept-encoding": "gzip"}
            req = urllib2.Request("http://fs-json.demo.vayant.com:7080/", data=json.dumps(request_json), headers=header)
            response = urllib2.urlopen(req)
            resp = self._decompress_and_extract_json(response)

            trip = self._get_flights_from_vayant_response(response)
            if trip:
                self.flights_resp_dal.remove(key)
                return None

            self.flights_resp_dal.set(key, trip)
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


    # def print_single_flight(self, flight):
    #     response = "\n"
    #     response += flight["Fares"][0]["Origin"] + " -> " + flight["Fares"][0]["Destination"] + ":\n"
    #     response += "total price = {}".format(flight['Price']['Total']['Amount']) + "\n"
    #     response += "flights details: "+ "\n"
    #     for leg in flight["Flights"]:
    #         response += "\t" + leg["Origin"] + " -> " + leg["Destination"] + ":"+ "\n"
    #         response += "\t departure: " + leg["Departure"]+ "\n"
    #         response += "\t arrival: " + leg["Arrival"]+ "\n"
    #         if self.flights_resp_dal.get_airline(leg["OperatingCarrier"]) is not None:
    #             response += "\t carrier: " + self.flights_resp_dal.get_airline(leg["OperatingCarrier"])+ "\n"
    #         else:
    #             response += "\t carrier: " + leg["OperatingCarrier"]+ "\n"
    #     return response


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
        for i in xrange(len(trip['Flights'])-1):
            if trip['Flights'][i]['Destination'] == connection:
                return trip['Flights'][i], trip['Flights'][i + 1]

        return None, None

    def get_price_round_trip(self, origin, dest, depart_dates, arrive_dates, get_full_response = False):
        first_trip = self.build_trip(origin, dest, depart_dates, 1)
        second_trip = self.build_trip(dest, origin, arrive_dates, 2)
        return self.get_flight_price_async([first_trip, second_trip])



    def get_price_one_way(self, origin, dest, depart_dates):
        first_trip = self.build_trip(origin, dest, depart_dates, 1)
        return self.get_flight_price_async([first_trip])


    def do_after_done(self, resp):
        trip_data = resp
        if trip_data and trip_data.has_key("Journeys") and trip_data['Journeys'] and len(trip_data['Journeys']) > 0:
            return self.extract_cheapest_price(trip_data), trip_data

        return (None, None)



