import queue
import time

# A global dictionary storing queues of tasks, organized by task name.
import psutil

from .taskIndexer import TaskIndexer

global_task_queue = TaskIndexer()

# Stores tuples of the form (<Thread name>, <Exception>) that should be handled by the main thread.
global_errors = queue.Queue()

# Stores the starting time of the job
start_time = time.time()

# Means threads should stop and join as soon as possible.
global_thread_stop_flag = [False]

# process class monitoring the job's ressource usage
global_process = psutil.Process()
