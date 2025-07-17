import cv2 as cv
import collections
import threading
import time

class FrameDisplay():
    """
    Synchronizes and prepares frames from multiple input queues.
    Combines them into a single frame and sends to display_frame_queue and crop_queue.
    """
    def __init__(self, thread_id, q, queue_id, caps, crop_queue, display_frame_queue, sync_threshold=0.1):
        self.thread_id = thread_id
        self.q = q
        self.queue_id = queue_id
        self.caps = caps
        self.crop_queue = crop_queue
        self.display_frame_queue = display_frame_queue
        self.sync_threshold = sync_threshold
        self.frame_counts = {} # Get timestamp of oldest frame in each buffer
        for qid in queue_id:
            self.frame_counts[qid] = 0
        self.buffers = {}
        for qid in queue_id:
            self.buffers[qid] = collections.deque(maxlen=10)
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
                    ts, frame = self.q[qid].get()
                    self.q[qid].task_done()
                    self.frame_counts[qid] += 1
                    self.buffers[qid].append((ts, self.frame_counts[qid], frame))

            if any(len(self.buffers[qid]) == 0 for qid in self.queue_id):
                continue

            # Sync based on median timestamp
            timestamps = [self.buffers[qid][0][0] for qid in self.queue_id]
            target_ts = sorted(timestamps)[len(timestamps) // 2]

            synced_frames = []
            for qid in self.queue_id:
                best_frame = None
                best_diff = float('inf')
                for ts, count, frame in self.buffers[qid]:
                    diff = abs(ts - target_ts)
                    if diff < best_diff and diff <= self.sync_threshold:
                        best_frame = (qid, count, frame)
                        best_diff = diff
                if best_frame:
                    synced_frames.append(best_frame)

            if len(synced_frames) != len(self.queue_id):
                continue

            labeled_frames = []
            for qid, count, frame in synced_frames:
                label = f"Frame-{count}"
                cv.putText(frame, label, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                labeled_frames.append(frame)

            combined = cv.hconcat(labeled_frames)
            scale = min(1.0, 1280 / combined.shape[1])
            combined_resized = cv.resize(combined,
                (int(combined.shape[1] * scale), int(combined.shape[0] * scale))
            )

            # Push frame to queues
            if not self.display_frame_queue.full():
                self.display_frame_queue.put(combined_resized)

            if not self.crop_queue.full():
                self.crop_queue.put(combined_resized)

        self.cleanup()
