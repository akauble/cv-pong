import time

class StopWatch:
    def __init__(self):
        self.start_time = 0
        self.stop_time = 0
        self.running = False

    def reset(self):
        self.running = False
        self.start_time = 0
        self.stop_time = 0

    def isRunning(self):
        return self.running

    def restart(self):
        self.reset()
        self.start()

    def start(self):
        self.running = True
        self.start_time = time.time()
        return self.start_time

    def stop(self):
        self.running = False
        self.stop_time = time.time()
        return self.stop_time

    def get_elapsed_time(self):
        if self.running:
            return time.time() - self.start_time
        else:
            return 0