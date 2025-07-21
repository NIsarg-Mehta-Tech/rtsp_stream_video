import queue
import threading
import time

class FrameCropped():
    """
    Thread to receive combined frames, crop center 400x400 region,
    and display the cropped window.
    """
    def __init__(self, thread_id, input_q):
        self.thread_id = thread_id
        self.input_q = input_q
        self.output_q = queue.Queue(maxsize = 5)
        self.thread = threading.Thread(target=self.run)
        self._stop_event = threading.Event()
        self.frame_count = 0
    
    def get_output_queue(self):
        return self.output_q
    
    def start(self):
        print(f"[Thread - {self.thread_id}] Started Cropping")
        self.thread.start()

    def join(self):
        self.thread.join()

    def stop(self):
        print(f"[Thread - {self.thread_id}] Stop signal received.")
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            if not self.input_q.empty():
                # Get combined frame from queue
                timestamp, count, frame = self.input_q.get()
                h, w = frame.shape[:2]
                crop_w = min(400,w) 
                crop_h = min(400,h)

                # Crop center 400x400 area
                start_x = (w - crop_w) // 2
                start_y = (h - crop_h) // 2
                cropped_frame = frame[start_y:start_y+crop_h, start_x:start_x+crop_w]
                self.frame_count += 1
                self.output_q.put((timestamp, count, cropped_frame))

                self.input_q.task_done()
            else:
                time.sleep(0.01)

        print(f"[Thread - {self.thread_id}] Cropping thread exited.")