import csv
from db.flights_resp import FlightsRespDAL
import connections_scraper

def insert_airlines_to_db(flights_dal):

    #remove all keys
    flights_dal.airline_collection.remove()

    with open('csv_files/airlines.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            try:
                if row[0] != "" and row[1] != "":
                    new_dict = {}
                    new_dict['airline_code'] = row[1]
                    new_dict['airline_name'] = row[0]
                    flights_dal.airline_collection.insert(new_dict)

            except:
                continue

def insert_airports_to_db(flights_dal):
    #remove all keys
    flights_dal.airport_collection.remove()

    with open('csv_files/all_airports', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                if row[1] != "" and row[3] != "" and row[4] != "" and row[6] != "" and row[7] != "" and len(row[4].strip('",')) < 5 and  len(row[4].strip('",')) > 1:
                    new_dict = {}
                    new_dict['airport_code'] = row[4].strip('",')
                    new_dict['airport_country'] = row[3].strip('",')
                    new_dict['airport_name'] = row[1].strip('",')
                    lat = float(row[6])
                    lng = float(row[7])
                    new_dict["area"] = flights_dal._get_area(lat, lng)
                    if new_dict["area"] != -1:
                        flights_dal.airport_collection.insert(new_dict)
            except Exception as e:
                print e
                continue


if __name__ == "__main__":
    flights_resp_dal = FlightsRespDAL()

    insert_airlines_to_db(flights_resp_dal)
    insert_airports_to_db(flights_resp_dal)

    #connections_scraper.scrap_connections(flights_resp_dal)
