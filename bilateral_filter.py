import threading
import time
import cv2 as cv
import queue

class BilateralFilter():
    def __init__(self, thread_id, input_q, output_q):
        self.thread_id = thread_id
        self.input_q = input_q
        self.output_q = output_q
        self.thread = threading.Thread(target=self.run)

    def start(self):
        print(f"[Thread {self.thread_id}] Started filtering.")
        self.thread.start()
    
    def join(self):
        self.thread.join()
    
    def run(self):
        while True:
            try:
                frame = self.input_q.get(timeout=5)
            except queue.Empty:
                print(f"[Thread - {self.thread_id}] No more frames exsist.")
                break

            print(f"[Thread-{self.thread_id}] Started")
        
            bila_filter = cv.bilateralFilter(frame, 9, 100, 100)
            self.output_q.put(bila_filter)
            self.input_q.task_done()
            time.sleep(0.5)
        
        print(f"[Thread-{self.thread_id}] Exiting bilateral filter thread.")