class Flight(object):
    def __init__(self, origin, dest, carrier, flight_number, departure, arrival):
        self.origin = origin
        self.dest = dest
        self.carrier = carrier
        self.flight_number = flight_number
        self.departure = departure
        self.arrival = arrival

class Trip(object):
    def __init__(self, price, legs):
        self.price = price
        self.legs = legs
