import pickle

from flights_data2.flight_search_manager import FlightSearchManager
from flights_data2.system_init import thread_pool, flight_provider, flight_resp_dal
from flights_data2.trip_data import TripDataRequest

if __name__ == "__main__":

    tests_to_run = []

    i=0
    with open("top_100_tests.info", "rU") as tests_file:
        while True:
            try:
                test = pickle.load(tests_file)
                i+=1
                tests_to_run.append(test)
            except EOFError:
                print "Finished loading %d tests" % i
                break

    #first time only for it to be entered to the DB, the second is for actual analyzing
    #tests_to_run = tests_to_run[0:300]
    for index, test in enumerate(tests_to_run):
        print test, index
        trip_data_request = TripDataRequest(*test)
        flight_search_manager = FlightSearchManager(trip_data_request, flight_provider, flight_resp_dal, thread_pool)
        flight_search_manager.search_all_flight_combinations()