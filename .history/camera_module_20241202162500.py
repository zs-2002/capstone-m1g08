import cv2

def capture_frame():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open camera")
    ret, frame = cap.read()
    cap.release()
    if ret:
        return frame
    else:
        raise Exception("Could not capture frame")
