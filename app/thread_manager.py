class ThreadMananager:
    def __init__(self):
        self.threads = []
    
    def add(self, thread_object):
        self.threads.append(thread_object)
    
    def start_all(self):
        for t in self.threads:
            t.start()
    
    def stop_all(self):
        for t in self.threads:
            t.stop()

    def join_all(self):
        for t in self.threads:
            t.join()

        print("All threads finished")