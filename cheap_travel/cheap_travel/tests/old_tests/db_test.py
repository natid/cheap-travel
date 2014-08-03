from flights_resp import FlightsRespDAL

if __name__ == "__main__":

    flights_resp_dal = FlightsRespDAL()
    flights_resp_dal.set("bla", {"a":1, "b":2, "c":3})

    data = flights_resp_dal.get("bla")
    assert data is not None

    flights_resp_dal.remove("bla")
    data = flights_resp_dal.get("bla")
    assert data is None

    a = flights_resp_dal.get("blaa")
    assert a is None


    print