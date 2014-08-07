from flights_data2.flight_search_manager import FlightSearchManager
from system_init import thread_pool, flight_provider, flight_resp_dal
from response_handler import ResponseHandler
from datetime import datetime
from trip_data import TripDataRequest
if __name__ == "__main__":
    response_handler = ResponseHandler()
    trip_data_request = TripDataRequest("TLV", "BKK", [datetime(2014,8,12)], [datetime(2014,8,22)])
    flight_search_manager = FlightSearchManager(trip_data_request, flight_provider, flight_resp_dal, thread_pool)
    flight_search_manager.add_observer(response_handler)
    flight_search_manager.search_all_flight_combinations()

