import queue
import time
from threading import Lock

# Stores Task instances waiting to be consumed.

tasks_queue = queue.Queue()

# Stores tuples of the form (<Thread name>, <Exception>) that should be handled by the main thread.
global_errors = queue.Queue()

# Stores the starting time of the job
start_time = time.time()

# Means threads should stop and join as soon as possible.
global_thread_stop_flag = [False]

# Keeps track of the number of a given job name stored in tasks_queue
job_counts_in_queue = [{}]
job_counts_in_queue_lock = Lock()
