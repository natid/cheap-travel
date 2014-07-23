from flask import Flask
from flask import request
import time
import thread
from flights_data.flight_checks import FlightChecker

import single_trip_tester

app = Flask(__name__)

result_for_user = None

@app.route("/")
def hello():
    response = "Single Trip Tester<br><br>" \
              '<form name="myform" action="http://127.0.0.1:5000/search" method="GET">' \
              'Origin:<br> <input type="text" name="origin" maxlength="5"><br>' \
              'Dest:<br> <input type="text" name="destination" maxlength="5"><br>' \
              'Departure Date:<br> <input type="date" name="departure_date"><br>' \
              'Return Date:<br> <input type="date" name="return_date"><br><br>' \
              '<input type="submit" value="search">' \
              '</form>'


    return response

@app.route("/search")
def get_results():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure_date')
    return_date = request.args.get('return_date')

    if origin and destination and departure_date and return_date:
        response = "you searched for a flight from {} to {} leaving at {} and returning at {}<BR><BR> we are working on it...".format(origin, destination, departure_date, return_date) + get_redirect_code()

        thread.start_new_thread(run_single_request, (origin, destination, departure_date, return_date))

        #for test
        #thread.start_new_thread(for_test_dummy_sleep,())
    else:
        response = "ERROR - missing parameters {},{},{},{}".format(origin, destination, departure_date, return_date)

    return response

def get_redirect_code():
     return '<script type="text/JavaScript">' \
            'redirectTime = "1500";' \
            'redirectURL = "http://127.0.0.1:5000/get_result";' \
            'function timedRedirect() {' \
            'setTimeout("location.href = redirectURL;",redirectTime);}'\
            'timedRedirect()</script>'

def for_test_dummy_sleep():
    global result_for_user
    time.sleep(10)
    result_for_user = "Success - only testing of course..."

def run_single_request(origin, destination, departure_date, return_date):
    global result_for_user

    start_time = time.time()
    flight_checker = FlightChecker()

    response = ""
    final_prices = single_trip_tester.get_single_check(origin, destination, departure_date, return_date, flight_checker)

    for cities, price in final_prices.iteritems():
        response += "{}, {}, price = {}, flights information is: \n".format(cities, price[0], price[1])
        for flight in price[2]:
            response += flight_checker.pricer.flights_provider.print_single_flight(flight)

    response += "total time it took = {}".format(time.time()-start_time)

    result_for_user = response

@app.route("/get_result")
def check_result():
    global result_for_user

    if result_for_user:
        return result_for_user
    else:
        return "Nothing Yet" + get_redirect_code()

if __name__ == "__main__":
    app.run()
