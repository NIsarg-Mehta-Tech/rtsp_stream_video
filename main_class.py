import cv2 as cv
import queue
from app.streamer_video import VideoStream
from app.bilateral_filter import BilateralFilter
from app.frame_display import FrameDisplay
from app.thread_manager import ThreadMananager
class RTSP_Video_Stream:
    def __init__(self, rtsp_urls):
        self.rtsp_urls = rtsp_urls
        self.n = len(rtsp_urls)
        self.queues = {i: queue.Queue() for i in range(1, 2 * self.n + 1)}
        self.caps = [cv.VideoCapture(url) for url in self.rtsp_urls]
        self.display = None
        self.thread_manager = ThreadMananager()
    
    def setup_threads(self):
        for i in range(self.n):
            stream_thread_id = 2 * i + 1
            filter_thread_id = 2 * i + 2

            stream = VideoStream(stream_thread_id, self.caps[i], self.queues[stream_thread_id])
            filt = BilateralFilter(filter_thread_id, self.queues[stream_thread_id], self.queues[filter_thread_id])

            self.thread_manager.add(stream)
            self.thread_manager.add(filt)
        
    def start(self):
        print("[App] Starting RTSP_Video_Stream")
        self.setup_threads()
        self.thread_manager.start_all()

        filtered_queue_ids = [2 * i + 2 for i in range(self.n)]
        self.display = FrameDisplay(self.queues, filtered_queue_ids, self.caps)
        self.display.run()

        self.cleanup()
    
    def cleanup(self):
        self.thread_manager.stop_all()
        self.thread_manager.join_all()
        print("All threads closed.")
        
if __name__ == "__main__":
    rtsp_urls = [
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0",
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0",
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0"
    ]

    app = RTSP_Video_Stream(rtsp_urls)
    app.start()