import cv2
from PIL import Image, ImageTk
import numpy as np
import time

class CameraModule:
    def __init__(self):
        self.cap = None  # Camera capture object
        self.running = False  # To track if the camera is running
        self.hand_detected_start = None  # Start time for hand detection
        self.total_hand_detected_time = 0  # Cumulative time hand is detected

    def start_feed(self, video_label):
        if not self.running:
            self.cap = cv2.VideoCapture(0)  # Open the default camera
            if not self.cap.isOpened():
                print("Error: Unable to access the camera.")
                return
            self.running = True
            self.hand_detected_start = None
            self.total_hand_detected_time = 0
            self._update_frame(video_label)

    def stop_feed(self):
        if self.running and self.cap is not None:
            self.running = False
            self.cap.release()  # Release the camera

            # Ensure detection time is recorded correctly when stopping
            if self.hand_detected_start is not None:
                self.total_hand_detected_time += time.time() - self.hand_detected_start
                self.hand_detected_start = None

            print(f"Total hand detection time: {self.total_hand_detected_time:.2f} seconds.")

    def _update_frame(self, video_label):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Resize the frame to a larger resolution (e.g., 640x480)
            frame = cv2.resize(frame, (480, 360))

            # Detect if a hand is present
            hand_detected = self.detect_hand(frame)

            # Manage hand detection timing
            if hand_detected:
                if self.hand_detected_start is None:
                    self.hand_detected_start = time.time()  # Start timing
            else:
                if self.hand_detected_start is not None:
                    self.total_hand_detected_time += time.time() - self.hand_detected_start
                    self.hand_detected_start = None

            # Convert frame to a format compatible with Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the video label
            video_label.imgtk = imgtk  # Keep a reference to avoid garbage collection
            video_label.config(image=imgtk)

        # Schedule the next frame update
        video_label.after(10, lambda: self._update_frame(video_label))

    def detect_hand(self, frame):
        """
        Detects if a hand is present in the frame.
        :param frame: Input frame from the video feed.
        :return: Boolean indicating if a hand is detected.
        """
        # Convert to HSV for better thresholding
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define skin color range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        # Threshold the HSV image to get only skin colors
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # Apply morphological transformations to filter noise
        mask = cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=1)
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)

        # Blur the mask to smooth the edges
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # If a significant contour is detected, return True
        for contour in contours:
            if cv2.contourArea(contour) > 1000:  # Threshold to avoid small contours
                return True

        return False
