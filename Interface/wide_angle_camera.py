import tkinter as tk
from camera_module import CameraModule

class WideAngleCameraInterface:
    def __init__(self):
        # Create a new Toplevel window
        self.window = tk.Toplevel()
        self.window.title("Wide-Angle Camera Interface")

        # Create a frame for the video feed
        self.video_frame = tk.Frame(self.window, bg="black", bd=2, relief="ridge")
        self.video_frame.pack(pady=10)
        self.video_label = tk.Label(self.video_frame, text="Video Feed", font=("Arial", 14), fg="white", bg="black")
        self.video_label.pack()

        # Camera module instance
        self.camera = CameraModule()

        # Start and stop buttons
        self.start_button = tk.Button(self.window, text="Start Camera", command=self.start_camera)
        self.start_button.pack(side="left", padx=10, pady=10)

        self.stop_button = tk.Button(self.window, text="Stop Camera", command=self.stop_camera)
        self.stop_button.pack(side="right", padx=10, pady=10)

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_camera(self):
        """Start the camera feed."""
        self.camera.start_feed(self.video_label)

    def stop_camera(self):
        """Stop the camera feed and reset the video label."""
        self.camera.stop_feed()
        self.video_label.config(image='', text="Video Feed", bg="black", fg="white")

    def on_closing(self):
        """Release camera resources before closing."""
        self.camera.stop_feed()
        self.window.destroy()
