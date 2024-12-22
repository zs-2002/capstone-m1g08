import cv2
from PIL import Image, ImageTk
import mediapipe as mp

class CameraModule:
    def __init__(self):
        self.cap = None  # Camera capture object
        self.running = False  # To track if the camera is running
        self.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,                # Detect up to 2 hands
            min_detection_confidence=0.5    # Adjust confidence as needed
        )

    def start_feed(self, video_label):
        if not self.running:
            self.cap = cv2.VideoCapture(1)  # Open the default camera
            if not self.cap.isOpened():
                print("Error: Unable to access the camera.")
                return
            self.running = True
            self._update_frame(video_label)

    def stop_feed(self):
        if self.running and self.cap is not None:
            self.running = False
            self.cap.release()  # Release the camera

    def _update_frame(self, video_label):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Resize the frame to a larger resolution (e.g., 640x480)
            frame = cv2.resize(frame, (480, 360))

            # Detect hands using MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mp_hands.process(frame_rgb)

            # Check if hands are detected and annotate the frame
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

            # Convert frame to a format compatible with Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the video label
            video_label.imgtk = imgtk  # Keep a reference to avoid garbage collection
            video_label.config(image=imgtk)

        # Schedule the next frame update
        video_label.after(10, lambda: self._update_frame(video_label))

    def get_current_frame(self):
        """Retrieve the current frame from the video feed."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
