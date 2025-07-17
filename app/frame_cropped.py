import threading
import time
import cv2 as cv

class FrameCropped():
    """
    Thread to receive combined frames, crop center 500x500 region,
    and display the cropped window.
    """
    def __init__(self, thread_id, crop_queue, display_crop_queue):
        self.thread_id = thread_id
        self.crop_queue = crop_queue
        self.display_crop_queue = display_crop_queue
        self.thread = threading.Thread(target=self.run)
        self._stop_event = threading.Event()

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
            if self.crop_queue.empty():
                time.sleep(0.01)
                continue
            
            # Get combined frame from queue
            frame = self.crop_queue.get()
            h, w = frame.shape[:2]
            crop_w = min(500,w) 
            crop_h = min(500,h)

            # Crop center 500x500 area
            start_x = (w - crop_w) // 2
            start_y = (h - crop_h) // 2
            cropped_frame = frame[start_y:start_y+crop_h, start_x:start_x+crop_w]

            if not self.display_crop_queue.full():
                self.display_crop_queue.put(cropped_frame)

            self.crop_queue.task_done()

        print(f"[Thread - {self.thread_id}] Cropping thread exited.")