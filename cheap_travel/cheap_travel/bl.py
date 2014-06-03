__author__ = 'magenn'

import utils
import vayant

def get_price_round_trip(origin, dest, depart_dates, arrive_dates):
    first_trip = vayant.build_trip(origin, dest, depart_dates, 1)
    second_trip = vayant.build_trip(dest, origin, arrive_dates, 2)
    trip_data = vayant.call_vayant([first_trip, second_trip])

    if not trip_data:
        return (None, None)


    return utils._extract_cheapest_price(trip_data), trip_data['Journeys'][0][0]

def get_price_one_way(origin, dest, depart_dates):
    first_trip = vayant.build_trip(origin, dest, depart_dates, 1)
    trip_data = vayant.call_vayant([first_trip])

    if not trip_data:
        return (None, None)

    return utils._extract_cheapest_price(trip_data), trip_data['Journeys'][0][0]

def get_connections(origin, dest):
    connection=set()
    single_trip = vayant.build_trip(origin, dest, "2014-12-18")

    go_trip_data = vayant.call_vayant([single_trip])
    if not go_trip_data:
        return
    return utils.get_connections_list(go_trip_data)

