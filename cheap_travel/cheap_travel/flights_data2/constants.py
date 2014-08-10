CONNECTION_DAYS = 4
THREAD_POOL_SIZE = 20
MAX_FLIGHTS_PER_TRIP = 20
DATE_FORMAT = "%Y-%m-%d"

PENDING = "pending"
ERROR_RESPONSE = "No Result"



# areas are in form of ([left upper corner], [right upper corner], [left bottom corner], [right bottom corner]], area index)
# all coordinates are in (latitude, longitude)

AREA_SOUTH_AMERICA = ([(14,-75), (-6,-20), (-72, -27), (-72, -85), (0, -85), (14,-75)], 1, "south_america")
AREA_CENTRAL_AMERICA = ([(32,-120), (25,-96), (21, -60), (14, -75), (0,-85), (32,-120)], 2, "central_america")
AREA_WEST_AMERICA = ([(84,-176), (84,-104), (29, -104), (24, -176), (84,-176)], 3, "west_america")
AREA_EAST_AMERICA = ([(84,-104), (84,-56), (24, -54), (24, -94), (29, -104), (84,-104)], 4, "east_america")
AREA_AFRICA = ([(33,-21), (30, 37), (-50, 65), (-40, -21), (33,-21)], 5, "africa")
AREA_EUROPE = ([(84,-56), (70, 47),(30, 37), (24, -54), (84,-56)], 6, "europe")
AREA_ASIA = ([(70,47), (72, 174), (10, 178), (30, 37), (70,47)], 7, "asia")
AREA_AUSTRALIA = ([(30,37), (10, 179), (24,179), (-51, 178), (-51, 65), (30,37)], 8, "australia")
AREA_PACIFIC_ISLANDS = ([(48,-177), (48, -130), (-60, -130), (-60, -177), (48,-177)], 9, "pacific islands")

areas = [AREA_SOUTH_AMERICA, AREA_CENTRAL_AMERICA, AREA_WEST_AMERICA, AREA_EAST_AMERICA, AREA_AFRICA, AREA_EUROPE, AREA_ASIA, AREA_AUSTRALIA, AREA_PACIFIC_ISLANDS]
