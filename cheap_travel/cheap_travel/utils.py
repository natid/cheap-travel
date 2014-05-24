__author__ = 'magenn'


import pprint
import csv
from collections import defaultdict
import threading
import time


airlines=defaultdict()
with open('airlines.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        try:
            if row[0] != "" and row[1] != "":
                airlines[row[1]] = row[0]
        except:
            continue

def get_price(resp):
    resp2 = sorted(resp['Journeys'], key=lambda trip: trip[0]['Price']['Total']['Amount'])
    try:
        return resp2[0][0]['Price']['Total']['Amount']
    except:
        return 0

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

def get_connections(origins, dests, func):

    for origin in origins:
         for dest in dests:
            if dest != origin:
                #single_check(origin, dest)
                while threading.activeCount() > 20:
                    time.sleep(5)
                t = threading.Thread(target=func, args=(str(origin).upper(), str(dest).upper()))
                t.start()

    while threading.activeCount() > 1:
        time.sleep(10)
