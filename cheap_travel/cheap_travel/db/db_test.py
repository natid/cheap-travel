from cheap_travel.db.flights_resp import FlightsRespDAL

if __name__ == "__main__":

    flights_resp_dal = FlightsRespDAL()
    flights_resp_dal.save_data("bla", {"a":1, "b":2, "c":3})

    a = flights_resp_dal.get_data("bla")
    print