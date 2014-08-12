from flights_data2.system_init import thread_pool, flight_provider, flight_resp_dal
from flights_data.flight_checks import FlightChecker
from pprint import pprint

def get_results_from_db():
    return flight_resp_dal.get_all_results()

def get_cheapest_flight(final_prices):
    found = False
    if final_prices:
        for flight in final_prices:
            if "Round Trip" in flight["type"]:
                round_trip_price = cheapest_trip_price = flight["price"]
                cheapest_flight = flight["flight"]
                cheapest_type = flight["type"]
                found  = True
                break
        if not found:
            print "couldn't find round trip"
            return None, None, None, None


        for flight in final_prices:
            if flight["price"] < cheapest_trip_price:
                cheapest_type = flight["type"]
                cheapest_trip_price = flight["price"]
                cheapest_flight = flight["flight"]

        return round_trip_price, cheapest_trip_price, cheapest_flight, cheapest_type
    else:
        return None, None, None, None

def get_chepaset_prices(results):
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

def get_upper_word(sentence):
    for word in sentence.split(" "):
        if word.isupper():
            return word
    return None

def get_prices_cheaper_than_round_trip(results_from_db, flight_checker):
    cheap_airports = {}
    expensive_airports = {}
    for index, result in enumerate(results_from_db):
        final_prices = result["connections"]
        origin = result["key"][0:3]
        dest = result["key"][4:7]
        area = flight_checker.pricer.flights_provider.flights_resp_dal.get_area_code(origin, dest)

        result = get_cheapest_flight(final_prices)
        round_trip_price = result[0]
        if not round_trip_price:
            continue

        for options in final_prices:
            for price in options:
                airport = get_upper_word(price[0])
                if airport:
                    if price[1] < round_trip_price:
                        if not cheap_airports.has_key(area):
                            cheap_airports[area] = set()
                        cheap_airports[area].add(airport)
                    else:
                        if not expensive_airports.has_key(area):
                            expensive_airports[area] = {}
                        if not expensive_airports[area].has_key(airport):
                            expensive_airports[area][airport] = list()
                        expensive_airports[area][airport].append((price[1]-round_trip_price)*100/round_trip_price)

    expensive_airports = clean_airports_which_are_cheaper(expensive_airports, cheap_airports)

    return cheap_airports, expensive_airports

def get_airports_that_can_be_removed(airports_cheaper, expensive_airports, flight_checker):
    can_be_removed = {}
    for i in range(10,100):
        area_code = "%s-%s" % (i/10, i%9 + 1)
        try:
            connections = flight_checker.pricer.flights_provider.flights_resp_dal.get_connections_in_area(area_code)[0]
        except:
            continue
        if airports_cheaper.has_key(area_code):
            for connection in airports_cheaper[area_code]:
                connections.remove(connection)
        can_be_removed[area_code] = connections

        for connection in connections:
            if not expensive_airports.has_key(area_code):
                expensive_airports[area_code] = {}
            if not expensive_airports[area_code].has_key(connection):
                expensive_airports[area_code][connection] = (0,0)



    return can_be_removed


def clean_airports_which_are_cheaper(expensive_airports, cheap_airports):
    new_expensive_airports = {}
    for i in range(10,100):
        area_code = "%s-%s" % (i/10, i%9 + 1)
        if expensive_airports.has_key(area_code):
            for airport, list_of_percentages in expensive_airports[area_code].iteritems():
                if not cheap_airports.has_key(area_code) or airport not in cheap_airports[area_code]:
                    if not new_expensive_airports.has_key(area_code):
                        new_expensive_airports[area_code] = {}
                    new_expensive_airports[area_code][airport] = (sum(list_of_percentages)/len(list_of_percentages), len(list_of_percentages), list_of_percentages)

    return new_expensive_airports


def check_which_connections_can_be_removed(results):
    flight_checker = FlightChecker()

    cheap_airports, expensive_airports = get_prices_cheaper_than_round_trip(results, flight_checker)
    can_be_removed = get_airports_that_can_be_removed(cheap_airports, expensive_airports, flight_checker)

    return can_be_removed, expensive_airports


def main():
    #run_tests_here


    #test 1
    results = get_results_from_db()
    trips_prices = get_chepaset_prices(results)
    total_saved = 0
    for result in trips_prices:
        print result[4], result[0], result[1], result[3]

    saved_in_average = calculate_average_percentage_saved(trips_prices)
    print saved_in_average, len(trips_prices)

    #test 2
    #check which connections can be removed
    # results = get_results_from_db()
    #
    # connections, expensive_airports = check_which_connections_can_be_removed(results)
    # pprint(connections)
    # pprint(expensive_airports)

if __name__ == "__main__":
    main()
