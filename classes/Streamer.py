import cv2
import numpy as np
from threading import Thread
import time
from queue import Queue
from constants import DEBUG,IS_LIVE
from datetime import datetime,timedelta
class Streamer:
    """
    Streamer handles RTSP video streaming and frame queuing for processing.
    """

    def __init__(self, rtsp) -> None:
        """
        Initialize the Streamer with an RTSP URL or camera index.
        Args:
            rtsp (str | int): RTSP stream URL or camera index.
        """
        print(f"Starting streaming {rtsp}")
        try:
            self.rtsp: int = int(rtsp)
        except ValueError:
            self.rtsp: str = rtsp
        self.stream: cv2.VideoCapture = cv2.VideoCapture(rtsp)
        self.DEBUG: bool = DEBUG
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.Q: Queue = Queue(maxsize=1)
        self.running: bool = True
        self.last_status_checked_time: datetime | None = None

    def start(self) -> None:
        """
        Start streaming frames and put them into the queue for processing.
        """
        print(f"Streamer object created for {self.rtsp}")
        count: int = 0
        while self.running:
            try:
                ret, frame = self.stream.read()
                if not ret:
                    print(f"NO Frame for {self.rtsp}")
                    continue
                if not IS_LIVE:
                    while self.Q.empty():
                        time.sleep(0.001)
                start_time = time.time()
                if not self.Q.full():
                    cv2.putText(frame, f"{count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.Q.put({"frame": frame, "counter": count, "stream": self.rtsp})
                    print("streaming_time", time.time() - start_time)
                count += 1
            except Exception as e:
                print(f"Error in Streamer: {e}")
                time.sleep(0.001)
        self.release()

    def stop(self) -> None:
        """
        Stop the streamer and release resources.
        """
        self.running = False
        self.release()

    def release(self) -> None:
        """
        Release the video stream resource.
        """
        self.stream.release()

    def info(self) -> None:
        """
        Print diagnostic information about the stream and its queue.
        """
        print("==============================Stream Info==============================")
        print(f"| Stream: {self.rtsp} |")
        print(f"| Queue Size: {self.Q.qsize()} |")
        print(f"| Running: {self.running} |")
        print("======================================================================")