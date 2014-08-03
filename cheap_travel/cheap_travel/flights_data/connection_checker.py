from flights_data.async_infrastructure.async_response import AsyncMultiResponse
from flights_data.async_infrastructure.response_collector import ResponseCollector
import time

class ConnectionChecker(object):
    def __init__(self, flight_checker, flights_resp_dal):
        self.flight_checker = flight_checker
        self.flights_resp_dal = flights_resp_dal
        self.resp_collector = ResponseCollector()

    def run_connection_check_async(self, origin, dest, depart_date, return_date):
        area = self.flights_resp_dal.get_area_code(origin, dest)
        connections_list = self.flights_resp_dal.get_connections_in_area(area)

        if len(connections_list) == 0:
            print "couldn't get connection list"
            return None


        for single_connection in connections_list[0]:
            if origin != dest != single_connection != origin:
                async_response = self.flight_checker.run_test_list(origin, dest, depart_date, return_date, single_connection, None)
                self.resp_collector.add_response(single_connection, "first", async_response)

        return AsyncMultiResponse(self.resp_collector)

    def run_connection_check(self, origin, dest, depart_date, return_date):
        async_resp = self.run_connection_check_async(origin, dest, depart_date, return_date)
        return async_resp.get_response()

