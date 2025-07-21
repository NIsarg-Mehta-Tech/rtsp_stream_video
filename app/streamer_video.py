import queue
import threading
import time
import cv2 as cv

class VideoStream():
    """
    Captures video frames from a source (e.g., RTSP stream) in a separate thread.
    Resizes frames and pushes them into an output queue with timestamps.
    """
    def __init__(self, thread_id, cap):
        self.thread_id = thread_id
        self.cap = cap  # OpenCV video capture object
        self.output_queue = queue.Queue(maxsize=5)
        self.thread = threading.Thread(target=self.run)
        self._stop_event = threading.Event()

    def get_output_queue(self):
        return self.output_queue
    
    def start(self):
        print(f"[Thread - {self.thread_id}] Started streaming.")
        self.thread.start()

    def join(self):
        self.thread.join()

    def stop(self):
        print(f"[Thread - {self.thread_id}] Stop signal received.")
        self._stop_event.set()

    def run(self):
        target_height = 480  # Resize height for standardization
        while self.cap.isOpened() and not self._stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                print(f"[Stream Thread - {self.thread_id}] Stream ended or was closed.")
                break

            # Resize frame to a standard height while preserving aspect ratio
            height_ratio = target_height / frame.shape[0]
            width = int(frame.shape[1] * height_ratio)
            frame_resized = cv.resize(frame, (width, target_height))

            # Push timestamped frame to output queue
            timestamp = time.time()
            self.output_queue.put((timestamp, frame_resized))
            print(f"[Thread - {self.thread_id}] Pushed frame to Queue-{self.thread_id}")

            # Sleep in small intervals so that stop can interrupt
            for _ in range(10):
                if self._stop_event.is_set():
                    break
                time.sleep(0.02)

        self.cap.release()
        print(f"[Thread - {self.thread_id}] Stream thread exited.")
