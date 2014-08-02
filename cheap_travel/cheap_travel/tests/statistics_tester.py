import pickle
from server.single_trip_tester import get_single_check
from flights_data.flight_checks import FlightChecker

def main(tests_name):
    tests_to_run = []
    prices = []

    i=0
    with open(tests_name, "rU") as tests_file:
        while True:
            try:
                test = pickle.load(tests_file)
                i+=1
                tests_to_run.append(test)
            except EOFError:
                print "Finished loading %d tests" % i
                break

    for index, test in enumerate(tests_to_run):
        print test, index
        final_prices = get_single_check(*test, flight_checker=FlightChecker())

if __name__ == "__main__":
    #main("tests.info")
    main("top_100_tests.info")