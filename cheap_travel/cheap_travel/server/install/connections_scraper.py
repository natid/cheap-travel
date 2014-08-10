from thread_pool import ThreadPool
from random import randint
from flights_data.flight_checks import FlightChecker
from datetime import timedelta
import datetime
import csv
from flights_data2.system_init import flight_provider, flight_resp_dal
from flights_data2.connection_flight_checks.flight_types import TwoOneWaysFlightType, RoundTripFlightType
from flights_data2.trip_data import TripDataRequest

def get_connections(origin, dest, date):

    trip_data_request = TripDataRequest(origin, dest, [date], [date])

    two_one_ways_trip_flight = TwoOneWaysFlightType(trip_data_request)
    flights_to_search = two_one_ways_trip_flight.get_trip_data_requests()

    flight1 = flights_to_search[0]

    response1 = flight_provider.search_flight(flight1)

    if response1:
        connections= get_connections_list(response1)

        area = get_area(origin, dest)
        flight_resp_dal.add_connections_to_area(area, connections)

def get_connections_list(response):
    connections = set()
    for single in response:
        if len(single["legs"]) == 2:
            if single["legs"][0]["dest"] == single["legs"][1]["origin"]:
                connections.add(single["legs"][0]["dest"])
    return connections

def get_area(origin, dest):
    return flight_resp_dal.get_area_code(origin, dest)

def scrap_connections():
    areas=set()
    airports = []
    with open('csv_files/top_100_airports.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for airport in row:
                airports.append(airport)

    origins = dests = airports

    dates = []

    for i in range(100):
        new_date = datetime.date(2014, 11, 02) + timedelta(days=i)
        dates.append(new_date)

    pool = ThreadPool(20)
    pool.start()
    for dest in dests:
        for origin in origins:
            if dest != origin:
                date = dates[randint(0, len(dates)-1)]
                pool.add_task(get_connections, origin, dest, date)
                areas.add(get_area(origin, dest))

    pool.wait_completion()

    #arrange all connections in single set per area instead of list
    areas_conn = dict()
    for area in areas:
        conn_list = flight_resp_dal.get_connections_in_area(area)
        connections = set()
        for conn in conn_list:
            connections.update(set(conn))
        areas_conn[area] = connections

    flight_resp_dal.clean_areas_to_connections_table()

    for area in areas:
        flight_resp_dal.add_connections_to_area(area, areas_conn[area])



if __name__ == "__main__":
    scrap_connections()