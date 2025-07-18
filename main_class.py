import cv2 as cv
import queue
from app.streamer_video import VideoStream
from app.bilateral_filter import BilateralFilter
from app.frame_cropped import FrameCropped
from app.frame_display import FrameDisplay
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
        self.raw_queues = {i: queue.Queue() for i in range(1, 2 * self.n + 1)}
        self.crop_queue = {i: queue.Queue() for i in range(1, self.n + 1)}
        self.caps = [cv.VideoCapture(url) for url in self.rtsp_urls]
        self.display_frame_queue = queue.Queue(maxsize=1)
        self.thread_manager = ThreadMananager()

        for idx, cap in enumerate(self.caps):
            if not cap.isOpened():
                print(f"[Error] Cannot open RTSP stream at index {idx}")
                raise RuntimeError("Failed to open one or more RTSP streams")
            
    def setup_threads(self):
        for i in range(self.n):
            stream_thread_id = 2 * i + 1
            filter_thread_id = 2 * i + 2

            stream = VideoStream(stream_thread_id, self.caps[i], self.raw_queues[stream_thread_id])
            
            filt = BilateralFilter(filter_thread_id, self.raw_queues[stream_thread_id], self.raw_queues[filter_thread_id])
            
            crop = FrameCropped(100 + i, self.raw_queues[filter_thread_id], self.crop_queue[i + 1])

            self.thread_manager.add(stream)
            self.thread_manager.add(filt)
            self.thread_manager.add(crop)

        display_thread_id = 2 * self.n + 1
        display = FrameDisplay(display_thread_id, self.crop_queue, list(self.crop_queue.keys()), self.caps, self.display_frame_queue)        

        self.thread_manager.add(display)
        self.display = display

    def start(self):
        print("[App] Strating RTSP Video Stream")
        self.setup_threads() 
        self.thread_manager.start_all()
        
        while True:
            if not self.display_frame_queue.empty():
                frame = self.display_frame_queue.get()
                cv.imshow("Combined Cropped Streams", frame)

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