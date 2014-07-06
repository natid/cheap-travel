from db.flights_resp import FlightsRespDAL
from datetime import timedelta, time, date
from flights_data.flight_checks import FlightChecker

def check_single(origin, dest, depart_date, return_date):

    round_trip_result = flight_checker.check_round_trip(origin, dest, depart_date, return_date, None, None)

    round_trip_price = round_trip_result[1]

    if not round_trip_result:
        print "ERROR"
        return

    dict_key = "%s-%s, %s, %s" % (origin, dest, depart_date, return_date)
    results = flight_checker.pricer.flights_provider.flights_resp_dal.get_results(dict_key)


    min_price = round_trip_price
    last_result = round_trip_result


    for single_result in results:
        for single_check in single_result:
            if min_price > single_check[1]:
                min_price = single_check[1]
                last_result = single_check

    print "for flight: {}-{} in {} until {}".format(origin, dest, depart_date, return_date)

    if min_price != round_trip_price:
        print "found cheeper price than round trip"
        print last_result
    else:
        print "didn't find cheeper price"
    print last_result

flight_checker = FlightChecker()



origin_list = ['LON', 'BER', 'AMS', 'ROM', 'PAR', 'ZRH']
dest_list = ['MNL', 'BKK', 'HKG', 'BJS']

depart_dates = [date(2014, 11, 02), date(2014, 9, 15), date(2015, 01, 01), date(2014, 07, 02), date(2014, 06, 25)]
return_dates = [depart_date  + timedelta(days=21) for depart_date in depart_dates]
return_dates += [depart_date  + timedelta(days=7) for depart_date in depart_dates]
return_dates += [depart_date  + timedelta(days=80) for depart_date in depart_dates]


for dest in dest_list:
    for origin in origin_list:
        for depart_date in depart_dates:
            for return_date in return_dates:
                if depart_date < return_date :
                    if origin != dest:
                        check_single(origin, dest, depart_date, return_date)



