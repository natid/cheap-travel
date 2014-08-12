from db.flights_resp import FlightsRespDAL
from flights_data2.constants import THREAD_POOL_SIZE
from flights_data2.flights_provider.vayant_flights_provider import VayantFlightsProvider
from flights_data2.queue_manager import MemoryQueueManager
from flights_data2.thread_pool2 import ThreadPool


#if __name__ == "__main__":
flight_resp_dal = FlightsRespDAL()
flight_provider = VayantFlightsProvider(flight_resp_dal)
thread_pool = ThreadPool(MemoryQueueManager(), THREAD_POOL_SIZE)

thread_pool.start()
