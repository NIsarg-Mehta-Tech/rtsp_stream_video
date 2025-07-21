import cv2 as cv
import queue
from app.streamer_video import VideoStream
from app.bilateral_filter import BilateralFilter
from app.frame_cropped import FrameCropped
from app.frame_difference import FrameDiff
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
        self.num_streams = len(rtsp_urls)
        self.thread_manager = ThreadMananager()
        self.display_frame_queue = queue.Queue(maxsize=1)
        self.process_layers = [BilateralFilter, FrameCropped, FrameDiff]
        
        self.final_output_queues = []
        
        self.caps = [cv.VideoCapture(url) for url in self.rtsp_urls]

        for idx, cap in enumerate(self.caps):
            if not cap.isOpened():
                print(f"[Error] Cannot open RTSP stream at index {idx}")
                raise RuntimeError("Failed to open one or more RTSP streams")
            
    def setup_threads(self):
        thread_id = 1

        for stream_idx in range(self.num_streams):
            cap = self.caps[stream_idx]

            stream_thread = VideoStream(thread_id, cap)
            self.thread_manager.add(stream_thread)
            thread_id += 1
            
            input_queue = stream_thread.get_output_queue()

            current_queue = input_queue
            for i, layer_cls in enumerate(self.process_layers):
                layer_thread = layer_cls(thread_id, current_queue)
                self.thread_manager.add(layer_thread)
                thread_id += 1
                current_queue = layer_thread.get_output_queue()

            self. final_output_queues.append(current_queue)

        # Display uses all prev and curr diff frames

        display = FrameDisplay(thread_id, {i: q for i, q in enumerate(self.final_output_queues)}, list(range(self.num_streams)), self.caps, self.display_frame_queue)
        self.thread_manager.add(display)

    def start(self):
        print("[App] Strating RTSP Video Stream")
        self.setup_threads() 
        self.thread_manager.start_all()
        
        while True:
            if not self.display_frame_queue.empty():
                final = self.display_frame_queue.get()
                cv.imshow("Difference Display", final)

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
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=3&subtype=0",
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=4&subtype=0"
    ]

    app = RTSP_Video_Stream(rtsp_urls)
    app.start()