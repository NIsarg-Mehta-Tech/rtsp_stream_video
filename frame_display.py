import cv2 as cv
import queue
class FrameDisplay():
    def __init__(self, q, queue_id, caps):
        self.q = q
        self.queue_id = queue_id
        self.caps = caps

    def run(self):
        frame_count = 0
        while True:
            frames = []
            for qid in self.queue_id:
                try:
                    frame = self.q[qid].get(timeout=5)
                    self.q[qid].task_done()
                    frames.append(frame)
                except queue.Empty:
                    print(f"[Display] Queue - {qid} is empty. Ending display")
                    return
                
            if not frames:
                break

            target_height = 480
            
            resized = [
                cv.resize(f, (int(f.shape[1] * target_height / f.shape[0]), target_height))
                for f in frames
            ]

            combined = cv.hconcat(resized)
            max_width = 1280
            scale = min(1.0, max_width / combined.shape[1])
            combined_resized = cv.resize(combined, (int(combined.shape[1] * scale), int(combined.shape[0] * scale)))

            cv.putText(combined_resized, f"Frame-{frame_count}", (10, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv.imshow("Combined Filtered Streams", combined_resized)

            if cv.waitKey(1) & 0xFF == ord('q'):
                print("[Display] 'q' pressed. Closing display.")
                break

            if cv.getWindowProperty("Combined Filtered Streams", cv.WND_PROP_VISIBLE) < 1:
                print("[Display] Window closed.")
                break

            frame_count += 1
        
        for cap in self.caps:
            cap.release()
        cv.destroyAllWindows()