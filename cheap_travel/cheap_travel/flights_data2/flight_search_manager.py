
class FlightPricesData(object):

    def __init__(self):
        self.connection_to_prices = {}
        self.roudtrip_price = None
        self.two_one_ways_price = None



class FlightSearchManager(object):

    def __init__(self, trip_data, flights_resp_dal):
        self.trip_data = trip_data
        self.origin = trip_data['origin']
        self.dest = trip_data['dest']
        self.depart_date = trip_data['depart_dates']
        self.return_date = trip_data['return_dates']
        self.flights_resp_dal = flights_resp_dal

    def search_flight(self):
        area = self.flights_resp_dal.get_area_code(self.origin, self.dest)
        connections_list = self.flights_resp_dal.get_connections_in_area(area)

        if len(connections_list) == 0:
            print "couldn't get connection list"
            return None

        self.send_requests_to_flight_provider(connections_list)




    def send_requests_to_flight_provider(self, connections_list):
        for single_connection in connections_list:



    '''
    def later(self):
        for single_connection in connections_list:
            if origin != dest != single_connection != origin:
                async_response = self.flight_checker.run_test_list(origin, dest, depart_date, return_date, single_connection, None)
                self.resp_collector.add_response(single_connection, "first", async_response)
    '''
    def get_flight_provider_request_list(self, connection):
        return [
                    (self.origin, self.dest, self.depart_date, self.return_date), # roundtrip
                    (self.origin, self.dest, self.depart_date), # two one ways
                    (self.dest, self.dest, self.depart_date), # two one ways


        ]

    def get_roundtrip_requests():

