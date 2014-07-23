from server.single_trip_tester import get_single_check

import pickle

final_prices = {}

if __name__ == "__main__":

    tests_to_run = []
    prices = []
    with open("tests.info", "rb") as tests_file:
        while True:
            try:
                test = pickle.load(tests_file)
                tests_to_run.append(test)
            except:
                break

    for test in tests_to_run:
        final_prices = get_single_check(*test)

        for cities, price in final_prices.iteritems():
            if "Round Trip" in price[0]:
                round_trip_price = price[1]
            else:
                cheapest_trip_price = price[1]
        prices.append((round_trip_price, cheapest_trip_price))

    total_precentage_saving = 0
    for price in prices:
        percentage_saved = (price[0] - price[1])/price[0]
        total_precentage_saving += percentage_saved

    saved_in_avergae = total_precentage_saving/len(prices)

    print saved_in_avergae

