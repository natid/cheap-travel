from db.flight_resp import FlightsRespDAL
from random import randint
from datetime import timedelta, date
import pickle

TESTS_TO_CREATE = 10000

flights_resp_dal = FlightsRespDAL()

airports = flights_resp_dal.get_all_airports()

tests = []
for index in xrange(0, TESTS_TO_CREATE):
    origin = airports[randint(0, len(airports))]
    dest = airports[randint(0, len(airports))]
    departure_date = date(2014, 8, 02) + timedelta(days=randint(0,130))
    return_date = departure_date+ timedelta(days=randint(0,40))

    tests.append((origin, departure_date, departure_date, return_date))


with open("tests.info", "w") as tests_file:
    for test in tests:
        pickle.dump(test,tests_file)

