import threading
import time
import cv2 as cv
import queue

class BilateralFilter():
    """
    Applies a bilateral filter to each incoming frame from input_q and sends
    the filtered frame with timestamp to output_q. Runs in a separate thread.
    """
    def __init__(self, thread_id, input_q):
        self.thread_id = thread_id
        self.input_q = input_q
        self.output_q = queue.Queue(maxsize=5)
        self.thread = threading.Thread(target=self.run)
        self._stop_event = threading.Event()
        self.frame_count = 0
    
    def get_output_queue(self):
        return self.output_q

    def start(self):
        print(f"[Thread - {self.thread_id}] Started filtering.")
        self.thread.start()
    
    def join(self):
        self.thread.join()

    def stop(self):
        print(f"[Thread - {self.thread_id}] Stop signal received.")
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            if not self.input_q.empty():
                # Get frame with timestamp
                timestamp, frame = self.input_q.get()
                print(f"[Thread - {self.thread_id}] Got frame from input queue.")
                self.frame_count += 1
                # Apply bilateral filter to the frame
                bila_filter = cv.bilateralFilter(frame, 10, 90, 90)
                self.output_q.put((timestamp, self.frame_count, bila_filter))
                print(f"[Thread - {self.thread_id}] Put filtered frame to output queue.")
                self.input_q.task_done()
            else:
                time.sleep(0.01)
           
        print(f"[Thread - {self.thread_id}] Exiting bilateral filter thread.")
