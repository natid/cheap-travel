from db.flights_resp import FlightsRespDAL
from datetime import timedelta, time, date
from flights_data.flight_checks import FlightChecker
from pprint import pprint
import tester

def check_single(origin, dest, depart_date, return_date):

    round_trip_result = flight_checker.check_round_trip(origin, dest, depart_date, return_date, None, None)

    round_trip_price = round_trip_result[1]

    if not round_trip_result:
        print "ERROR"
        return

    dict_key = "%s-%s, %s, %s" % (origin, dest, depart_date, return_date)
    results = flight_checker.pricer.flights_provider.flights_resp_dal.get_results(dict_key)

    if not results:
        #print "ERROR - no result in DB"
        return


    min_price = round_trip_price
    last_result = round_trip_result


    for single_result in results:
        for single_check in single_result:
            if min_price > single_check[1]:
                min_price = single_check[1]
                last_result = single_check


    if min_price != round_trip_price:
        # print "for flight: {}-{} in {} until {}".format(origin, dest, depart_date, return_date)
        # print "found cheeper price than round trip"
        # print "round trip price = {}, cheapest price found = {}, diff = {}, percentage = {}%".format(round_trip_price, min_price,
#                                                                                                     round_trip_price - min_price, (round_trip_price - min_price)*100/round_trip_price)
        nir = ((round_trip_price - min_price)*100/round_trip_price, round_trip_price, min_price, (origin, dest, depart_date, return_date),last_result[0] )
        #print nir
        return nir
    else:
        pass#print "didn't find cheeper price"
    #print last_result

if __name__ == "__main__":
    flight_checker = FlightChecker()

    results=[]

    sum = 0
    num = 0
    all = 0
    for dest in tester.dest_list:
        for origin in tester.origin_list:
            for depart_date in tester.depart_dates:
                for return_date in tester.return_dates:
                    if depart_date < return_date :
                        if origin != dest:
                            result = check_single(origin, dest, depart_date, return_date)
                            if result:
                                results.append(result)
                                sum += result[0]
                                all +=1
                            num +=1

pprint(sorted(results, reverse=True))

print sum/num
print num
print all


