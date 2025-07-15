import cv2
import os
from threading import Thread
from classes.Streamer import Streamer
from classes.ImageProcessor import ImageProcessor
from typing import List,Dict

class ThreadManger:
    """
    ThreadManger manages multiple RTSP streamers and image processors using threads.
    It handles thread creation, frame concatenation, and visualization.
    """

    def __init__(self, urls: list[str]) -> None:
        """
        Initialize the ThreadManger with a list of RTSP URLs.
        Args:
            urls (list[str]): List of RTSP stream URLs.
        """
        self.urls: list[str] = urls
        self.objects: dict[str, dict] = dict()
        self.daemon: bool = True
        self.__init_objects__()
        self.running: bool = True

    def __init_objects__(self) -> None:
        """
        Initialize streamer and processor objects for each URL.
        """
        for url in self.urls:
            print(f"Initializing objects for {url}")
            self.objects[url] = {
                "streamer": {"object": Streamer(url), "thread": None},
                "processor": {"object": ImageProcessor(), "thread": None}
            }

    def start(self) -> None:
        """
        Start all streamer and processor threads.
        """
        for url in self.objects:
            self.objects[url]["streamer"]["thread"] = Thread(target=self.objects[url]["streamer"]["object"].start)
            self.objects[url]["streamer"]["thread"].daemon = self.daemon
            self.objects[url]["streamer"]["thread"].start()
            self.objects[url]["processor"]["thread"] = Thread(target=self.objects[url]["processor"]["object"].start, args=(self.objects[url]["streamer"]["object"].Q,))
            self.objects[url]["processor"]["thread"].daemon = self.daemon
            self.objects[url]["processor"]["thread"].start()

    def concat_frame(self, frames: list) -> any:
        """
        Concatenate all frames horizontally from the list of frames.
        Args:
            frames (list): List of frames to concatenate.
        Returns:
            concatenated_frame: The horizontally concatenated frame.
        """
        concatenated_frame = cv2.hconcat(frames)
        return concatenated_frame

    def start_visualizer(self) -> None:
        """
        Visualize concatenated frames from all streams in a window.
        """
        while self.running:
            frames = []
            print(len(self.objects), "streams are running")
            for url in self.objects:
                data = self.objects[url]["processor"]["object"].writer_queue.get()
                if data is None:
                    continue
                frame = data["processed_frame"]
                counter = data["counter"]
                frames.append(frame)
            if frames:
                print(len(frames), "frames received for concatenation")
                concatenated_frame = self.concat_frame(frames)
                cv2.namedWindow("Concatenated Stream", cv2.WINDOW_NORMAL)
                cv2.imshow("Concatenated Stream", concatenated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    def stop(self) -> None:
        """
        Stop all streamer and processor threads and release resources.
        """
        self.running = False
        for url in self.objects:
            self.objects[url]["streamer"]["object"].stop()
            self.objects[url]["processor"]["object"].stop()
        cv2.destroyAllWindows()


        
if __name__ == "__main__":
    # urls = [0]
    urls = ["rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0",
            "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=4&subtype=0",
            "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=6&subtype=0",
            "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=7&subtype=0",
            "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=8&subtype=0"]
    try:
        manager_object = ThreadManger(urls)
        manager_object.start()
        manager_object.start_visualizer()
    except KeyboardInterrupt:
        manager_object.stop()  