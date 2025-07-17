import cv2 as cv
import queue
from app.streamer_video import VideoStream
from app.bilateral_filter import BilateralFilter
from app.frame_display import FrameDisplay
from app.frame_cropped import FrameCropped
from thread_manager.thread_manager import ThreadMananager
class RTSP_Video_Stream:
    """
    The main controller class that sets up:
    - RTSP streams
    - Bilateral filtering threads
    - Display with synchronization
    - Thread management (start, stop, cleanup)
    """
    def __init__(self, rtsp_urls):
        self.rtsp_urls = rtsp_urls
        self.n = len(rtsp_urls)
        self.queues = {i: queue.Queue() for i in range(1, 2 * self.n + 1)}
        self.caps = [cv.VideoCapture(url) for url in self.rtsp_urls]
        self.crop_queue = queue.Queue(maxsize=5)
        self.display_frame_queue = queue.Queue(maxsize=1)
        self.display_crop_queue = queue.Queue(maxsize=1)
        self.thread_manager = ThreadMananager()

        for idx, cap in enumerate(self.caps):
            if not cap.isOpened():
                print(f"[Error] Cannot open RTSP stream at index {idx}")
                raise RuntimeError("Failed to open one or more RTSP streams")
            
    def setup_threads(self):
        for i in range(self.n):
            stream_thread_id = 2 * i + 1
            filter_thread_id = 2 * i + 2

            stream = VideoStream(stream_thread_id, self.caps[i], self.queues[stream_thread_id])
            filt = BilateralFilter(filter_thread_id, self.queues[stream_thread_id], self.queues[filter_thread_id])

            self.thread_manager.add(stream)
            self.thread_manager.add(filt)

    
        display_thread_id = 2 * self.n + 1
        filtered_queue_ids = [2 * i + 2 for i in range(self.n)]
        display = FrameDisplay(display_thread_id, self.queues, filtered_queue_ids, self.caps, self.crop_queue, self.display_frame_queue)
        self.thread_manager.add(display)
        self.display = display

        crop_thread_id = 2 * self.n + 2
        cropper = FrameCropped(crop_thread_id, self.crop_queue, self.display_crop_queue)  
        self.thread_manager.add(cropper)

    def start(self):
        print("[App] Strating RTSP Video Stream")
        self.setup_threads() 
        self.thread_manager.start_all()
        
        while True:
            if not self.display_frame_queue.empty():
                frame = self.display_frame_queue.get()
                cv.imshow("Combined Filtered Streams", frame)
            
            if not self.display_crop_queue.empty():
                crop_frame = self.display_crop_queue.get()
                cv.imshow("Cropped Frame", crop_frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                print("[Main] Quit requested from GUI.")
                break
        
        self.cleanup()

    def cleanup(self):
        self.thread_manager.stop_all()
        self.thread_manager.join_all()
        cv.destroyAllWindows()
        print("All threads closed.")

if __name__ == "__main__":
    rtsp_urls = [
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0",
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0",
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0"
    ]

    app = RTSP_Video_Stream(rtsp_urls)
    app.start()