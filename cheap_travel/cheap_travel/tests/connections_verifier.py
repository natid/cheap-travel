
from db.flights_resp import FlightsRespDAL
import constants

if __name__ == "__main__":
    flights_resp_dal = FlightsRespDAL()

    connections_by_areas = flights_resp_dal.connections_collection.find()


    for area1 in constants.areas:
        for area2 in constants.areas:
            key = "%s-%s" % (area1[1], area2[1])
            connections = flights_resp_dal.get_connections_in_area(key)

            print "----------------------------"
            print "connections for flights from {} to {}".format(area1[2], area2[2])
            if connections:
                for connection in connections[0]:
                    airport = flights_resp_dal.get_airport(connection)
                    if airport:
                        print "code = {}, airport = {}, country = {}".format(connection, airport[0], airport[1])
                    else:
                        print "unknown details for airport code {}".format(connection)