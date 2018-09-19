from .client import *
from SocialNetworkHarvester.settings import LOG_DIRECTORY, DEBUG
import os


class CommonThread(threading.Thread):
    lastQueueSize = 0

    def __init__(self, threadName):
        super().__init__()
        self.name = threadName
        if not hasattr(self, 'batchSize'):
            raise Exception('batchsize must be defined')
        if not hasattr(self, 'method'):
            raise Exception('method must be defined')
        if not hasattr(self, 'workQueueName'):
            raise Exception('workQueueName must be defined')

    def run(self):
        try:
            log('starting',showTime=True)
            self.execute()
            log('finished gracefully',showTime=True)
        except ExitFlagRaised:
            log('finished gracefully', showTime=True)
        except Exception as e:
            exceptionQueue.put((e, self.name))
            log('%s HAS ENCOUNTERED AN ERROR' % threading.current_thread().name.upper())
        finally:
            return 0

    def execute(self):
        batch = []
        while True:
            time.sleep(0.5)
            if threadsExitFlag[0]:
                break
            elif not self.workQueue().empty():
                item = self.workQueue().get()
                batch.append(item)
                if len(batch) >= self.batchSize:
                    self.logWorkQueueStatus()
                    #log('batch: %s'%batch)
                    self.method(batch)
                    batch = []
            elif len(batch) > 0:
                self.logWorkQueueStatus()
                self.method(batch)
                batch = []

    def logWorkQueueStatus(self):
        if abs(self.lastQueueSize - self.workQueue().qsize()) >= 50:
            self.lastQueueSize = self.workQueue().qsize()
            log('remaining items in workQueue (%s): %s' % (self.workQueue()._name, self.workQueue().qsize()))

    def workQueue(self):
        return globals()[self.workQueueName]

    def clearBatch(self, batch):
        for item in batch:
            del item
        return []
