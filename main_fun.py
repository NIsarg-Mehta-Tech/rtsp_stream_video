import threading
import time
import queue
import cv2 as cv

n = 3
no_thread = 2 * n + 1
no_queue = 2 * n

def create_queues():
    queues = {}
    for i in range(1, no_queue +1):
        queues[i] = queue.Queue()
    return queues

def create_threads():
    threads = {}
    for i in range(1, no_thread + 1):  
        threads[i] = None
    return threads

def stream_video(thread_id, output_queue, cap):
   
    while cap.isOpened():
           
        ret, frame = cap.read()
        
        if not ret:
            break

        output_queue.put(frame)
        print(f"[Thread-{thread_id}] Pushed frame to Queue-{thread_id}")
        time.sleep(0.2)

    print(f"[Thread-{thread_id}] Exiting stream thread.")
    cap.release()

def bilateral_filter(thread_id, input_q, output_q):
    frame_count = 0

    while True:
        try:
            frame = input_q.get(timeout=5)
        except queue.Empty:
            print(f"[Thread - {thread_id}] No more frames exsist.")
            break 
        print(f"[Thread-{thread_id}] Started")
        
        bila_filter = cv.bilateralFilter(frame, 9, 100, 100)

        output_q.put(bila_filter)
        frame_count += 1
        time.sleep(0.5)
        input_q.task_done()
        print(f"[Thread-{thread_id}] Exiting bilateral filter thread.")

def display_frames(q, queue_id, caps):
    frame_count = 0
    while True:
        frames = []

        for qid in queue_id:
            try:
                frame = q[qid].get(timeout=5)
                frames.append(frame)
                q[qid].task_done()
            except queue.Empty:
                print(f"[Display] Queue - {qid} is empty. Ending display")
                return
        combined = cv.hconcat(frames)

        target_width = 1200
        scale = target_width / combined.shape[1]
        resized_combined = cv.resize(combined, (target_width, int(combined.shape[0] * scale)))

        cv.putText(combined, f"Queue-{queue_id} Frame-{frame_count}", (10, 40),
                   cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)

        cv.imshow("Combined Filtered Streams", resized_combined)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[Display] Quit requested.")
            for cap in caps:
                cap.release()
            break
        frame_count += 1
    cv.destroyAllWindows()

def main():
    queues = create_queues()
    threads = create_threads()

    rtsp_url1 = "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0"
    rtsp_url2 = "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0"
    rtsp_url3 = "rtsp://admin:abc%401234@192.168.0.248:554/cam/realmonitor?channel=2&subtype=0"
    caps = [
            cv.VideoCapture(rtsp_url1), 
            cv.VideoCapture(rtsp_url2), 
            cv.VideoCapture(rtsp_url3) 
            ]
    for i in range(n):  
        stream_thread_id = 2 * i + 1  
        stream_queue_id = 2 * i + 1  

        filter_thread_id = 2 * i + 2  
        filter_queue_id = 2 * i + 2  

        print(f"\n[Stream] Thread-{stream_thread_id}, Queue-{stream_queue_id}")
        
        threads[stream_thread_id] = threading.Thread(target=stream_video, args=(stream_thread_id, queues[stream_queue_id], caps[i]))
        threads[stream_thread_id].start()
               
        threads[filter_thread_id] = threading.Thread(target=bilateral_filter, args=(filter_thread_id, queues[stream_queue_id], queues[filter_queue_id]))
        threads[filter_thread_id].start()
        
    filter_queue_ids = [2 * i + 2 for i in range(n)]
    display_frames(queues, filter_queue_ids, caps)
  

    for t in threads.values():
        if t:
            t.join()

    print("All threads end.")

if __name__ == "__main__":
    main()  