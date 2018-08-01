import sys
from Queue import Queue
import threading
from threading import Thread

_thread_print_lock = threading.Lock()

"""
https://www.metachris.com/2016/04/python-threadpool/
"""
class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks, tasks_mutex):
        Thread.__init__(self)
        self.tasks = tasks
        self.mutex = tasks_mutex
        self.daemon = True
        self.start()

    def run(self):
        while True:
            with self.mutex:
                func, args, kargs = self.tasks.get()
            try:
                with _thread_print_lock:
                    print "inside worker"
                    print func
                    print args
                    print kargs
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print "# An exception happened in this thread"
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        self.tasks_mutex = threading.Lock()
        for _ in range(num_threads):
            print "prepare worker"
            Worker(self.tasks, self.tasks_mutex)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        print "add task"
        print func
        print args
        print kargs
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


if __name__ == "__main__":
    from random import randrange
    from time import sleep

    # Function to be executed in a thread
    def wait_delay(d):
        print("sleeping for (%d)sec" % d)
        while (d > 0):
            print "Sleep 1s in", threading.current_thread()
            sleep(1)
            d -= 1

    # Generate random delays
    delays = [randrange(3, 7) for i in range(50)]

    # Instantiate a thread pool with 5 worker threads
    pool = ThreadPool(5)

    # Add the jobs in bulk to the thread pool. Alternatively you could use
    # `pool.add_task` to add single jobs. The code will block here, which
    # makes it possible to cancel the thread pool with an exception when
    # the currently running batch of workers is finished.
    pool.map(wait_delay, delays)
    pool.wait_completion()
    