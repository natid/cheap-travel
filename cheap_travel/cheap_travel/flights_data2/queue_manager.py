from Queue import Queue


class BaseQueueManager(object):

    def put(self, data):
        pass

    def get(self):
        pass

    def task_done(self):
        pass


class MemoryQueueManager(BaseQueueManager):

    def __init__(self):
        self.queue = Queue()

    def put(self, data):
        self.queue.put(data)

    def get(self):
        return self.queue.get()

    def task_done(self):
        self.queue.task_done()




