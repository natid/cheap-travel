__author__ = 'magenn'


import csv
from collections import defaultdict
from Queue import Queue
from threading import Thread
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

def extract_cheapest_price(resp):
    sorted_response = sorted(resp['Journeys'], key=lambda trip: trip[0]['Price']['Total']['Amount'])
    try:
        return sorted_response[0][0]['Price']['Total']['Amount']
    except:
        print "ERROR getting the price" , resp, sorted_response
        return 0

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, pool, worker_number, added_name=None, added_class=None):
        Thread.__init__(self)
        self.pool = pool
        self.tasks = pool.tasks
        self.worker_number = worker_number
        self.daemon = True
        self.added_kargs = {}

        if added_class:
            self.added_instance = added_class()
            self.added_name = added_name

    def add_to_kargs(self, name, value):
        self.added_kargs[name] = value

    def run(self):
        while True:
            func, task_number, args, kargs = self.tasks.get()
            kargs[self.added_name] = self.added_instance
            print "worker number {0} going to do task number {1}".format(self.worker_number, task_number)
            duration = 0
            try:
                start_time = time.time()
                func(*args, **kargs)
                duration = time.time() - start_time
            except Exception, e:
                print e
            finally:
                self.tasks.task_done()
                self.pool.task_ended(self.worker_number, task_number, duration)

class ThreadPool(object):
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads=1, added_name=None, added_class=None):
        self.tasks = Queue()
        self.workers = []
        for i in xrange(1, num_threads+1):
            self.workers.append(Worker(self, i, added_name, added_class))
        self.task_number = 0

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.task_number += 1
        self.tasks.put((func, self.task_number, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

    def start(self):
        for worker in self.workers:
            worker.start()

    def task_ended(self, worker_number, task_number, duration):
        self.task_number -= 1
        print "worker number {0} finished task number {1}, " \
              "Number of open tasks is {2}, " \
              "the duration is {3}".format(worker_number, task_number, self.task_number, duration)





