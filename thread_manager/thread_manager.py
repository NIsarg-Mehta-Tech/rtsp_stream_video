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
        print("[ThreadManager] Starting all threads...")
        for t in self.threads:
            t.start()
        print("[ThreadManager] All threads started.")
    
    def stop_all(self):
        print("[ThreadManager] Stopping all threads...")
        for t in self.threads:
            t.stop()
        print("[ThreadManager] All stop signals sent.")

    def join_all(self):
        print("[ThreadManager] Waiting for all threads to finish...")
        for t in self.threads:
            t.join()
        print("[ThreadManager] All threads finished")