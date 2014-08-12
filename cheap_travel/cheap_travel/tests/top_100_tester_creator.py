import pickle
import datetime
from random import randint
import pickle

TESTS_TO_CREATE = 10000

with open("../server/install/csv_files/top_100_airports.csv") as f:
    airports = f.read().split((","))

tests = []
for index in xrange(0, TESTS_TO_CREATE):
    origin = airports[randint(0, len(airports)-1)]
    dest = airports[randint(0, len(airports)-1)]
    departure_date = datetime.date(2014, 8, 22) + datetime.timedelta(days=randint(0,130))
    return_date = departure_date+ datetime.timedelta(days=randint(5,40))

    tests.append((origin, dest, [departure_date], [return_date]))


with open("top_100_tests.info", "w") as tests_file:
    for test in tests:
        pickle.dump(test,tests_file)

