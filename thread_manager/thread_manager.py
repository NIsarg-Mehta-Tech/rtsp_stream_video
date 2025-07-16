class ThreadMananager:
    """
    A simple utility class to manage multiple threads:
    - Start all
    - Stop all (via user-defined stop methods)
    - Join all (wait for all threads to finish)
    """
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