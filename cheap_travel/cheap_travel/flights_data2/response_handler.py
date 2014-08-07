from flights_data2.observer import Observer


class ResponseHandler(Observer):

    def update(self, flight_search_manager, *args, **kwargs):
        if kwargs['finished'] is True:
            self.handle_finished()
            return

        self.handle_cheap_price(flight_search_manager)

    def handle_cheap_price(self, flight_search_manager):
        print flight_search_manager.flight_response

    def handle_finished(self):
        print "FINISHED!!!"



