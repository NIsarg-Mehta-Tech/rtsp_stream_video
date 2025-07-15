import cv2 as cv
import queue
from streamer_video import VideoStream
from bilateral_filter import BilateralFilter
from frame_display import FrameDisplay

def main():
    n = 3
    rtsp_urls = [
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0",
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0",
        "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0"
    ]

    queues = {i: queue.Queue() for i in range(1, 2 * n + 1)}
  
    caps = [cv.VideoCapture(url) for url in rtsp_urls]

    streams = []
    filters = []

    for i in range(n):
        stream_thread_id = 2 * i + 1
        filter_thread_id = 2 * i + 2

        stream = VideoStream(stream_thread_id, caps[i], queues[stream_thread_id])
        filt = BilateralFilter(filter_thread_id, queues[stream_thread_id], queues[filter_thread_id])

        stream.start() 
        filt.start()

        streams.append(stream)
        filters.append(filt)

    display = FrameDisplay(queues, [2 * i + 2 for i in range(n)], caps)
    display.run()

    for stream in streams:
        stream.join()

    for filt in filters:
        filt.join()

    print("All threads end.")

if __name__ == "__main__":
    main()  