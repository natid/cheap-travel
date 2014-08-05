from Queue import Queue
from threading import Thread
import time
import traceback

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, pool, worker_number):
        Thread.__init__(self)
        self.pool = pool
        self.tasks = pool.tasks
        self.worker_number = worker_number
        self.daemon = True

    def run(self):
        while True:
            func, task_number, args, kargs = self.tasks.get()
            #print "worker number {0} going to do task number {1}".format(self.worker_number, task_number)
            duration = 0
            try:
                start_time = time.time()
                func(*args, **kargs)
                duration = time.time() - start_time
            except Exception, e:
                print e
                traceback.print_exc()
            finally:
                self.tasks.task_done()
                self.pool.task_ended(self.worker_number, task_number, duration)


class ThreadPool(object):
    """Pool of threads consuming tasks from a queue"""

    def __init__(self, queue, num_threads=1):
        self.tasks = queue()
        self.workers = []
        for i in xrange(1, num_threads + 1):
            self.workers.append(Worker(self, i))
        self.task_number = 0

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.task_number += 1
        self.tasks.put((func, self.task_number, args, kargs))

    def start(self):
        for worker in self.workers:
            worker.start()

    def task_ended(self, worker_number, task_number, duration):
        self.task_number -= 1
        print "worker number {0} finished task number {1}, " \
              "Number of open tasks is {2}, " \
              "the duration is {3}".format(worker_number, task_number, self.task_number, duration)


