from flights_data.async_infrastructure.async_response import AsyncMultiResponse
from flights_data.async_infrastructure.response_collector import ResponseCollector
from flights_data.flight_checks import FlightChecker
from db.flights_resp import FlightsRespDAL


class ConnectionChecker(object):
    def __init__(self, vayant_connector):
        self.flight_checker = FlightChecker(vayant_connector)
        self.flights_resp_dal = FlightsRespDAL()
        self.resp_collector = ResponseCollector()

    def get_dict_key(self, origin, dest, depart_date, return_date):
        return "%s-%s, %s, %s" % (origin, dest, depart_date, return_date)

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
        dict_key = self.get_dict_key(origin, dest, depart_date, return_date)
        cached_result = self.flights_resp_dal.get_results(dict_key)

        if cached_result:
            return cached_result

        async_resp = self.run_connection_check_async(origin, dest, depart_date, return_date)
        res = async_resp.get_response()

        dict_key = self.get_dict_key(origin, dest, depart_date, return_date)
        self.flights_resp_dal.insert_results_to_db(dict_key, res)

        return res
