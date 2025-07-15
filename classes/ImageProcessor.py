import cv2
import numpy as np
from threading import Thread
import time
from queue import Queue
from constants import DEBUG,IS_LIVE
from datetime import datetime,timedelta

class ImageProcessor:
    """
    ImageProcessor handles frame processing in a threaded pipeline.
    It reads frames from a reader queue, processes them, and writes results to a writer queue.
    """

    def __init__(self) -> None:
        """
        Initialize the ImageProcessor with default settings and queues.
        """
        self.running: bool = True
        self.reader_queue: Queue | None = None
        self.writer_queue: Queue = Queue(maxsize=1)
        self.DEBUG: bool = DEBUG

    def start(self, reader_queue: Queue) -> None:
        """
        Start processing frames from the reader_queue.
        Args:
            reader_queue (Queue): Queue containing frames to process.
        """
        self.reader_queue = reader_queue
        while self.running:
            try:
                if self.reader_queue and not self.reader_queue.empty():
                    data: dict = self.reader_queue.get()
                    frame = data["frame"]
                    counter = data["counter"]
                    stream = data["stream"]

                    if self.DEBUG:
                        print(f"Processing frame {counter} from stream {stream}")

                    processed_frame = cv2.bilateralFilter(
                        frame, 15, 90, 90
                    )
                    data['processed_frame'] = processed_frame
                    if not self.writer_queue.full():
                        self.writer_queue.put(data)
                else:
                    time.sleep(0.001)
            except Exception as e:
                print(f"Error in ImageProcessor: {e}")
                time.sleep(0.001)

    def stop(self) -> None:
        """
        Stop the image processor loop.
        """
        self.running = False

    def info(self) -> None:
        """
        Print diagnostic information about the processor and its queues.
        """
        print("==============================Image Processor Info==============================")
        print(f"| Queue Size: {self.writer_queue.qsize()} |")
        print(f"| Running: {self.running} |")
        print("======================================================================")
    