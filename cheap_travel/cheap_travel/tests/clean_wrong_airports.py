from thread_pool import ThreadPool
from db.flights_resp import FlightsRespDAL
from flights_data.flight_checker import FlightChecker
from datetime import date

airports_error = []

def check_flights(origin, dest,  depart_date, flight_checker):
    if not flight_checker.pricer.get_price_one_way(origin, dest, str(depart_date))[0]:
        airports_error.append(dest)


pool = ThreadPool(20, "flight_checker", FlightChecker)

flight_resp_dal = FlightsRespDAL()

depart = date(2014, 8, 02)
dests = flight_resp_dal.get_all_airports()
print len(dests)
for dest in dests:
    pool.add_task(check_flights, "JFK", dest, depart)
pool.start()
pool.wait_completion()

print airports_error

for y in airports_error:
    flight_resp_dal.airport_collection.remove({"airport_code": y})
