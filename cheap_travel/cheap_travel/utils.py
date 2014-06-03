__author__ = 'magenn'


import csv
from collections import defaultdict
import threading
import time
import Queue


airlines=defaultdict()
with open('airlines.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        try:
            if row[0] != "" and row[1] != "":
                airlines[row[1]] = row[0]
        except:
            continue


def print_trip(trip):
    for flight in trip['Journeys'][0:1]:
        print_single_flight(flight[0])

def print_single_flight(flight):
    #print flight["Fares"][0]
    print flight["Fares"][0]["Origin"] + " -> " + flight["Fares"][0]["Destination"] + ":"
    print "total price = {}".format(flight['Price']['Total']['Amount'])
    print "flights details: "
    for leg in flight["Flights"]:
        print "\t" + leg["Origin"] + " -> " + leg["Destination"] + ":"
        print "\t departure: "+ leg["Departure"]
        print "\t arrival: " + leg["Arrival"]
        if airlines.has_key(leg["OperatingCarrier"]):
            print "\t carrier: " + airlines[leg["OperatingCarrier"]]
        else:
            print "\t carrier: " + leg["OperatingCarrier"]

def get_connections_list(trip):
    connections=set()
    for single in trip['Journeys']:
        if len(single[0]["Flights"]) == 2 :
            if single[0]["Flights"][0]["Destination"] == single[0]["Flights"][1]["Origin"]:
                connections.add(single[0]["Flights"][0]["Destination"])
    return connections

def read_airport_codes_from_csv():
    origins=[]
    with open('airport-codes.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            try:
                if row[0] != "" :
                    origins.append(row[0])
            except:
                continue

    return origins

def _create_str_date(date):
    return date.strftime("%Y-%m-%d")

def get_departure_flight_date(trip_response):
    return trip_response['Flights'][0]['Departure'][0:10]

def get_return_flight_date(trip_response):
    return trip_response['Flights'][-1]['Departure'][0:10]

def _extract_cheapest_price(resp):
    sorted_response = sorted(resp['Journeys'], key=lambda trip: trip[0]['Price']['Total']['Amount'])
    try:
        return sorted_response[0][0]['Price']['Total']['Amount']
    except:
        print "ERROR getting the price" , resp, sorted_response
        return 0

