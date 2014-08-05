from Queue import Queue


class BaseQueueManager(object):

    def put(self, data):
        pass

    def get(self):
        pass


class MemoryQueueManager(BaseQueueManager):

    def __init__(self):
        self.queue = Queue()

    def put(self, data):
        self.queue.put(data)

    def get(self):
        self.queue.get()




