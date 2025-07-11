import threading
import time
import cv2 as cv

class VideoStream():
    def __init__(self, thread_id, cap, output_queue):
        self.thread_id = thread_id
        self.cap = cap
        self.output_queue = output_queue
        self.thread = threading.Thread(target=self.run)

    def start(self):
        print(f"[Thread-{self.thread_id}] Started streaming.")
        self.thread.start()

    def join(self):
        self.thread.join()

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print(f"[Stream Thread - {self.thread_id}] Stream ended or was closed.")
                break

            self.output_queue.put(frame)
            print(f"[Thread-{self.thread_id}] Pushed frame to Queue-{self.thread_id}")
            time.sleep(0.2)

        self.cap.release()
        print(f"[Thread-{self.thread_id}] Stream thread exited.")
