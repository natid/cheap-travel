from dateutil import parser
from constants import DATE_FORMAT

class TripDataRequest(object):

    def __init__(self, origin, dest, depart_dates, return_dates=None):
        self.origin = origin
        self.dest = dest
        self.depart_dates = depart_dates
        self.return_dates = return_dates

    def compute_key(self):
        words_to_join = [self.origin, self.dest]

        for date in self.depart_dates:
            words_to_join.append(date.strftime(DATE_FORMAT))

        if self.return_dates:
            for date in self.return_dates:
                words_to_join.append(date.strftime(DATE_FORMAT))

        return "-".join(words_to_join)

class TripDataResponse(object):
    def __init__(self, dict_response):
        self.trips = [Trip(**trip) for trip in dict_response]

    def get_cheapest_flight_and_price(self):
        sorted_flights = sorted(self.trips, key=lambda trip: trip.price)
        try:
            return sorted_flights[0].price, sorted_flights[0]
        except:
            print "ERROR getting the cheapest flight"
            return (None, None)

class Trip(object):
    def __init__(self, price, legs):
        self.price = price
        self.legs = [Flight(**leg) for leg in legs]

    def get_dest_arrival_and_departure_flights_in_two_way(self, dest):
        for i in xrange(len(self.legs)-1):
            if self.legs[i].dest == dest:
                return self.legs[i], self.legs[i+1]
        return None, None

    def __repr__(self):
        to_return = "\n"
        to_return += "price:{}".format(self.price)
        for leg in self.legs:
            to_return +="\nleg: "
            to_return += str(leg)

        return to_return

    def to_dict(self):
        to_return = self.__dict__
        to_return["legs"] = [x.to_dict() for x in self.legs]
        return to_return

class Flight(object):
    def __init__(self, origin, dest, departure, arrival, carrier, flight_number):
        self.origin = origin
        self.dest = dest
        self.departure = departure
        self.arrival = arrival
        self.carrier = carrier
        self.flight_number = flight_number

    def __repr__(self):
        to_return = ""
        to_return += "origin={}, dest={}, departure={}, arrival={}, carrier={}, flight_number={}" \
            .format(self.origin, self.dest, self.departure, self.arrival, self.carrier, self.flight_number)

        return to_return

    def to_dict(self):
        return self.__dict__

    def flights_can_connect(self, flight):
        if not flight:
            return False

        #first check that it's the same airport
        #TODO - see how we handle airport changes in the connections
        if (self.dest != flight.origin):
            return False

        #then check that there's a 5 hour connection time (#TODO - why 5?)
        arrival_time = parser.parse(self.arrival)
        deparure_time = parser.parse(flight.departure)
        delta = deparure_time - arrival_time

        if (delta.total_seconds() / 60 / 60 < 0):
            return False

        return True

