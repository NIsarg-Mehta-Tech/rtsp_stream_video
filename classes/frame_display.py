import cv2 as cv
import collections
import threading
import time

class FrameDisplay():
    """
    Synchronizes and prepares prev/curr cropped frames from multiple input queues.
    Combines them into a 2x3 grid frame and sends to display_frame_queue.
    """
    def __init__(self, thread_id, q, queue_id, caps, display_frame_queue):
        self.thread_id = thread_id
        self.q = q
        self.queue_id = queue_id
        self.caps = caps
        self.display_frame_queue = display_frame_queue
        self.prev_frames = {qid: None for qid in queue_id}
        self.curr_frames = {qid: None for qid in queue_id}
        self.counts = {qid: 0 for qid in queue_id}
        self.thread = threading.Thread(target=self.run)
        self._stop_event = threading.Event()
    
    def start(self):
        print(f"[Thread - {self.thread_id}] Started Display")
        self.thread.start()

    def stop(self):
        print(f"[Thread - {self.thread_id}] Stopped Display")
        self._stop_event.set()
    
    def join(self):
        self.thread.join()

    def cleanup(self):
        # Release all video sources and clear OpenCV display
        for cap in self.caps:
            cap.release()
        for qid in self.queue_id:
            with self.q[qid].mutex:
                self.q[qid].queue.clear()
        cv.destroyAllWindows()

    def run(self):
        print("[Display] Started synced display.")
        while not self._stop_event.is_set():
            # Fill frame buffers
            for qid in self.queue_id:
                while not self.q[qid].empty():
                    ts, count, prev, curr = self.q[qid].get()
                    self.q[qid].task_done()
                    self.prev_frames[qid] = prev
                    self.curr_frames[qid] = curr
                    self.counts[qid] = count

            if any(self.prev_frames[qid] is None or self.curr_frames[qid] is None for qid in self.queue_id):
                time.sleep(0.01)
                continue

            # Build top and bottom row (Prev / Curr)
            prev_frames = []
            curr_frames = []

            for qid in self.queue_id:
                count = self.counts[qid]
                prev = self.prev_frames[qid].copy()
                curr = self.curr_frames[qid].copy()
                label_prev = f"[{qid}] Prev-{count - 5}"
                label_curr = f"[{qid}] Curr-{count}"
                
                cv.putText(prev, label_prev, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv.putText(curr, label_curr, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                prev_frames.append(prev)
                curr_frames.append(curr)

            row1 = cv.hconcat(prev_frames)
            row2 = cv.hconcat(curr_frames)
            combined = cv.vconcat([row1, row2])

            scale = min(1.0, 1280 / combined.shape[1])
            combined_resized = cv.resize(combined,
                (int(combined.shape[1] * scale), int(combined.shape[0] * scale))
            )

            # Push frame to queues
            if not self.display_frame_queue.full():
                self.display_frame_queue.put(combined_resized)

            time.sleep(1 / 30)

        self.cleanup()
