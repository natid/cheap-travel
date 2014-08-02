from flights_data.flight_checks import FlightChecker
from server.single_trip_tester import get_cheapest_flight
from time import time
def get_results_from_db():
    return FlightChecker().pricer.flights_provider.flights_resp_dal.get_all_results()

def get_chepaset_prices():
    results = get_results_from_db()
    prices = []

    for index, result in enumerate(results):
        final_prices = result["connections"]
        round_trip_price, cheapest_trip_price, cheapest_flight, cheapest_type = get_cheapest_flight(final_prices)
        #get_cheapest_flight only returns values if there was a round trip price
        if round_trip_price and cheapest_trip_price:
            prices.append((round_trip_price, cheapest_trip_price, cheapest_flight, cheapest_type, result["key"]))

    return prices

def calculate_average_percentage_saved(prices):
    total_precentage_saving = 0
    for price in prices:
        print price[4], price[0], price[1], price[3]
        percentage_saved = (price[0] - price[1])*100/price[0]
        total_precentage_saving += percentage_saved
    saved_in_average = total_precentage_saving/len(prices)

    return saved_in_average


def main():
    trips_prices = get_chepaset_prices()
    print len(trips_prices)

    #run_tests_here
    saved_in_avergae = calculate_average_percentage_saved(trips_prices)
    print saved_in_avergae, len(trips_prices)


if __name__ == "__main__":
    main()