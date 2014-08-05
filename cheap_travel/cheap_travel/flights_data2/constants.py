from flights_data2.flights_provider.vayant_flights_provider import VayantFlightsProvider
from flights_data2.queue_manager import MemoryQueueManager

CONNECTION_DAYS = 4


FLIGHT_PROVIDER_QUEUE = MemoryQueueManager()
FLIGHT_PROVIDER = VayantFlightsProvider()