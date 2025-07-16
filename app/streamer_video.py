import threading
import time
import cv2 as cv

class VideoStream():
    def __init__(self, thread_id, cap, output_queue):
        self.thread_id = thread_id
        self.cap = cap
        self.output_queue = output_queue
        self.thread = threading.Thread(target=self.run)
        self._stop_event = threading.Event()

    def start(self):
        print(f"[Thread-{self.thread_id}] Started streaming.")
        self.thread.start()

    def join(self):
        self.thread.join()
    
    def stop(self):
        print(f"[Thread-{self.thread_id}] Stop signal received.")
        self._stop_event.set()

    def run(self):
        target_height = 480
        while self.cap.isOpened() and not self._stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                print(f"[Stream Thread - {self.thread_id}] Stream ended or was closed.")
                break

            height_ratio = target_height / frame.shape[0]
            width =  int(frame.shape[1] * height_ratio)
            frame_resized = cv.resize(frame, (width, target_height))

            timestamp = time.time()
            self.output_queue.put((timestamp, frame_resized))
            print(f"[Thread-{self.thread_id}] Pushed frame to Queue-{self.thread_id}")
            
            for _ in range(10):
                if self._stop_event.is_set():
                    break
                time.sleep(0.02)

        self.cap.release()
        print(f"[Thread-{self.thread_id}] Stream thread exited.")
