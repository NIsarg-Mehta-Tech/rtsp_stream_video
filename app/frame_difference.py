import queue
import threading
import time
import cv2 as cv

class FrameDiff():
    def __init__(self, thread_id, input_q):
        self.thread_id = thread_id
        self.input_q = input_q
        self.output_q = queue.Queue(maxsize=5)
        self.thread = threading.Thread(target=self.run)
        self._stop_event = threading.Event()
        self.prev_frame = None

    def get_output_queue(self):
        return self.output_q

    def start(self):
        print(f"[Thread - {self.thread_id}] Starting FrameDiff thread")
        self.thread.start()
    
    def join(self):
        self.thread.join()
    
    def stop(self):
        print(f"[Thread - {self.thread_id}] Stopping FrameDiff thread")
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            if not self.input_q.empty():
                timestamp, count, curr_frame = self.input_q.get()
                if self.prev_frame is None:
                    self.prev_frame = curr_frame.copy()
                    self.input_q.task_done()
                    continue

                self.output_q.put((timestamp, count, self.prev_frame.copy(), curr_frame))                
                self.prev_frame = curr_frame.copy()
                
                self.input_q.task_done()
            else:
                time.sleep(0.01)
        
        print(f"[Thread - {self.thread_id}] FrameDiff thread exited.")
        