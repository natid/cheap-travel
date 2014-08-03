import pickle
import datetime
from server.single_trip_tester import get_single_check, get_cheapest_flight
from flights_data.flight_checker import FlightChecker

if __name__ == "__main__":

    tests_to_run = []
    prices = []

    i=0
    with open("tests.info", "rU") as tests_file:
        while True:
            try:
                test = pickle.load(tests_file)
                i+=1
                tests_to_run.append(test)
            except EOFError:
                print "Finished loading %d tests" % i
                break

    #first time only for it to be entered to the DB, the second is for actual analyzing
    tests_to_run = tests_to_run[0:300]
    for index, test in enumerate(tests_to_run):
        print test, index
        final_prices = get_single_check(*test, flight_checker=FlightChecker())
        if not final_prices:
            tests_to_run.remove(test)

    with open("updated_tests.info", "w") as tests_file:
        for test in tests_to_run:
            pickle.dump(test,tests_file)

    for index, test in enumerate(tests_to_run):
        print test, index
        final_prices = get_single_check(*test, flight_checker=FlightChecker())
        round_trip_price, cheapest_trip_price, flight, cheapest_type = get_cheapest_flight(final_prices)
        if round_trip_price and cheapest_trip_price:
            prices.append((round_trip_price, cheapest_trip_price))

    total_precentage_saving = 0
    for price in prices:
        percentage_saved = (price[0] - price[1])/price[0]
        total_precentage_saving += percentage_saved

    saved_in_avergae = total_precentage_saving/len(prices)

    print saved_in_avergae, len(prices)
