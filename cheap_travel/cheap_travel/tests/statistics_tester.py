import pickle
import datetime
from server.single_trip_tester import get_single_check, get_cheapest_flight
from flights_data.flight_checks import FlightChecker

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


    for test in tests_to_run:
        print test
        final_prices = get_single_check(*test, flight_checker=FlightChecker())

        round_trip_price, cheapest_trip_price, flight, cheapest_type = get_cheapest_flight(final_prices)
        prices.append((round_trip_price, cheapest_trip_price))

    total_precentage_saving = 0
    for price in prices:
        percentage_saved = (price[0] - price[1])/price[0]
        total_precentage_saving += percentage_saved

    saved_in_avergae = total_precentage_saving/len(prices)

    print saved_in_avergae, len(prices)
