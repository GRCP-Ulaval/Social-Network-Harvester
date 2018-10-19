import queue
import time

# Stores Task instances waiting to be consumed.

tasks_queue = queue.Queue()

# Stores tuples of the form (<Thread>, <Exception>) that should be handled by the main thread.
global_errors = queue.Queue()

# Stores the starting time of the job
start_time = time.time()

# Means threads should stop and join as soon as possible.
global_thread_stop_flag = [False]

