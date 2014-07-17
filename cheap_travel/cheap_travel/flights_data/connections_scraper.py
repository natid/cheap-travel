from thread_pool import ThreadPool
from random import randint
from flights_data.flight_checks import FlightChecker
from datetime import timedelta, date

def get_connections(origin, dest, date, flight_checker):

    go_trip_data = flight_checker.pricer.get_price_one_way(origin, dest, date)[1]
    connections= flight_checker.pricer.flights_provider.get_connections_list(go_trip_data)

    flight_checker.pricer.flights_provider.flights_resp_dal.add_connections_to_area(get_area(flight_checker, origin, dest), connections)


def get_area(flight_checker, origin, dest):
    return flight_checker.pricer.flights_provider.flights_resp_dal.get_area_code(origin, dest)


if __name__ == "__main__":
    areas=set()
    flight_checker = FlightChecker()
    origins = dests = flight_checker.pricer.flights_provider.flights_resp_dal.get_all_airports()

    dates = []

    for i in range(100):
        new_date = date(2014, 11, 02) + timedelta(days=i)
        dates.append(new_date.strftime("%Y-%m-%d"))


    pool = ThreadPool(20, "flight_checker", FlightChecker)

    for dest in dests:
        for origin in origins:
            if dest != origin:
                date = dates[randint(0, len(dates)-1)]
                pool.add_task(get_connections, origin, dest, date)
                areas.add(get_area(flight_checker, origin, dest))

    pool.start()
    pool.wait_completion()


    #arrange all connections in single set per area instead of list
    areas_conn = dict()
    for area in areas:
        conn_list = flight_checker.pricer.flights_provider.flights_resp_dal.get_connections_in_area(area)
        connections = set()
        for conn in conn_list:
            connections.add(conn)
        areas_conn[area] = connections

    flight_checker.pricer.flights_provider.flights_resp_dal.clean_areas_to_connections_table()

    for area in areas:
        flight_checker.pricer.flights_provider.flights_resp_dal.add_connections_to_area(area, areas_conn[area])



