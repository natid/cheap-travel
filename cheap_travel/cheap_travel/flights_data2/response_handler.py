from flights_data2.observer import Observer


class ResponseHandler(Observer):

    def update(self, flight_search_manager, *args, **kwargs):
        if 'finished' in kwargs:
            self.handle_finished()
            return

        self.handle_cheap_price(flight_search_manager, kwargs['flight_type'])

    def handle_cheap_price(self, flight_search_manager, flight_type=None):
        print flight_search_manager.cheapest_flight
        print flight_type.get_flight_type_str()

    def handle_finished(self):
        print "FINISHED!!!"



