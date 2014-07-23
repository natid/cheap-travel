from flask import Flask
from flask import request
import time
import thread

import single_trip_tester

app = Flask(__name__)

@app.route("/")
def hello():
    response = "Single Trip Tester<br><br>"
    response +=  '<form name="myform" action="http://127.0.0.1:5000/search" method="GET">'
    response +=  'Origin:<br> <input type="text" name="origin" maxlength="5"><br>'
    response +=  'Dest:<br> <input type="text" name="destination" maxlength="5"><br>'
    response +=  'Departure Date:<br> <input type="date" name="departure_date"><br>'
    response +=  'Return Date:<br> <input type="date" name="return_date"><br><br>'
    response += '<input type="submit" value="search">'
    response += '</form>'

    return response

@app.route("/search")
def get_results():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure_date')
    return_date = request.args.get('return_date')

    if origin and destination and departure_date and return_date:
        response = "you searched for a flight from {} to {} leaving at {} and returning at {}<BR><BR> we are working on it...".format(origin, destination, departure_date, return_date)

        #thread.start_new_thread(run_single_request, (origin, destination, departure_date, return_date))
    else:
        response = "ERROR - missing parameters {},{},{},{}".format(origin, destination, departure_date, return_date)

    return response

def run_single_request(origin, destination, departure_date, return_date):
    start_time = time.time()

    response = ""
    final_prices = single_trip_tester.get_single_check(origin, destination, departure_date, return_date)

    for cities, price in final_prices.iteritems():
        response += "{}, {}, price = {}, flights information is: \n".format(cities, price[0], price[1])
        for flight in price[2]:
            response += flight_checker.pricer.flights_provider.print_single_flight(flight)

    response += "total time it took = {}".format(time.time()-start_time)


if __name__ == "__main__":
    app.run()
