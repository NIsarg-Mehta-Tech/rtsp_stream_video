import cv2 as cv
import queue
import time
import collections
class FrameDisplay():
    def __init__(self, q, queue_id, caps, sync_threshold=0.1):

        self.q = q
        self.queue_id = queue_id
        self.caps = caps
        self.sync_threshold = sync_threshold
        self.frame_counts = {}
        for qid in queue_id:
            self.frame_counts[qid] = 0
        self.buffers = {}
        for qid in queue_id:
            self.buffers[qid] = collections.deque(maxlen=10)


    def cleanup(self):
        for cap in self.caps:
            cap.release()

        for qid in self.queue_id:
            with self.q[qid].mutex:
                self.q[qid].queue.clear()
        cv.destroyAllWindows()



    def run(self):
        print("[Display] Started synced display.")

        while True:

            for qid in self.queue_id:
                try:
                    while True:
                        ts, frame = self.q[qid].get_nowait()
                        self.q[qid].task_done()
                        self.frame_counts[qid] += 1
                        count = self.frame_counts[qid]
                        self.buffers[qid].append((ts, count, frame))

                except queue.Empty:
                    continue

            any_empty = False
            for qid in self.queue_id:
                if len(self.buffers[qid]) == 0:
                    any_empty = True
                    break

            if any_empty:
                continue


            timestamps = []
            for qid in self.queue_id:
                ts, _, _ = self.buffers[qid][0]  # Get timestamp of oldest frame in each buffer
                timestamps.append(ts)

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
                cv.putText(frame, label, (10, 30), cv.FONT_HERSHEY_SIMPLEX,
                           1, (0, 255, 0), 2)
                labeled_frames.append(frame)


            combined = cv.hconcat(labeled_frames)

            scale = min(1.0, 1280 / combined.shape[1])
            combined_resized = cv.resize(combined,
                (int(combined.shape[1] * scale), int(combined.shape[0] * scale))
            )

            try:
                cv.imshow("Combined Filtered Streams", combined_resized)
            except cv.error as e:
                print(f"[Display] OpenCV imshow error: {e}")

            if cv.waitKey(1) & 0xFF == ord('q'):
                print("[Display] Quit requested.")
                break

        self.cleanup()
