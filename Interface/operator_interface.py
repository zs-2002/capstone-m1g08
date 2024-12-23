import tkinter as tk
import pandas as pd
import threading
import cv2
import socket
from detection_script import start_detection
from check_step_cam import CameraModule


class OperatorInterface:
    def __init__(self, selected_process, parent_interface):
        self.window = tk.Toplevel()
        self.window.title("Operator and Detection Interface")
        self.parent_interface = parent_interface  # Reference to the parent interface

        # Set up the main layout
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(fill="both", expand=True)

        # Left Frame: Operator Interface
        self.left_frame = tk.Frame(self.main_frame, width=400)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Right Frame: Detection Interface
        self.right_frame = tk.Frame(self.main_frame, width=600)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Attributes
        self.steps = []
        self.current_step = 0
        self.total_time = 0
        self.detection_running = True
        self.logged_data = []

        # Socket communication attributes
        self.rpi_host = "192.168.137.121"  # Replace with Raspberry Pi's IP address
        self.rpi_port = 5000
        self.socket = None

        # Load the ROI from CSV
        self.roi_coordinates = self.load_roi_coordinates()

        # Load steps from supervisor based on selected process
        self.load_process_steps(selected_process)

        # Operator Interface in Left Frame
        self.operator_camera_module = CameraModule()
        self.setup_operator_interface()

        # Detection Interface in Right Frame
        self.detection_camera_module = CameraModule()
        self.setup_detection_interface()

        # Establish socket connection to Raspberry Pi
        self.connect_to_rpi()

        # Bind cleanup function to close window
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_roi_coordinates(self):
        """Load the last row of ROI coordinates from CSV."""
        try:
            df = pd.read_csv("roi_coordinates.csv")
            roi = df.iloc[-1].tolist()  # Get the last row
            print(f"Loaded ROI from last row: {roi}")
            return roi
        except FileNotFoundError:
            print("ROI file not found.")
            return None
        except Exception as e:
            print(f"Error loading ROI: {e}")
            return None

    def load_process_steps(self, selected_process):
        """Load process steps for the operator interface."""
        try:
            df = pd.read_csv("assembly_steps.csv")
            self.steps = df[df['process'] == selected_process].to_dict("records")
        except FileNotFoundError:
            print("Error: No steps defined!")

    def connect_to_rpi(self):
        """Establish a socket connection to the Raspberry Pi."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.rpi_host, self.rpi_port))
            print(f"Connected to Raspberry Pi at {self.rpi_host}:{self.rpi_port}")
        except Exception as e:
            print(f"Error connecting to Raspberry Pi: {e}")
            self.socket = None

    def send_angles_to_rpi(self, h_angle, v_angle):
        """Send angles to the Raspberry Pi via socket."""
        try:
            if self.socket:
                data = f"{1},{h_angle},{v_angle}"  # Format: <camera_id>,<h_angle>,<v_angle>
                self.socket.sendall(data.encode("utf-8"))
                print(f"Sent angles to RPi: {data}")
        except Exception as e:
            print(f"Error sending angles to RPi: {e}")

    def setup_operator_interface(self):
        """Set up the operator interface in the left frame."""
        tk.Label(self.left_frame, text="Operator Interface", font=("Arial", 16)).pack(pady=10)

        # Step display
        self.step_label = tk.Label(self.left_frame, text="Current Step: ", font=("Arial", 14))
        self.step_label.pack(pady=10)

        # Correctness display
        self.correctness_display = tk.Text(self.left_frame, height=15, width=40, font=("Arial", 12))
        self.correctness_display.pack(pady=10)

        # Alert display
        self.alert_label = tk.Label(self.left_frame, text="", font=("Arial", 14), fg="red")
        self.alert_label.pack(pady=10)

        # Video feed label for the operator
        self.operator_video_label = tk.Label(self.left_frame, bg="black", text="Operator Feed")
        self.operator_video_label.pack(pady=10)

        # Add a "Back to Supervisor Interface" button
        tk.Button(self.left_frame, text="Back to Supervisor Interface", command=self.navigate_back).pack(pady=10)

        # Start the operator feed
        self.start_operator_feed()

    def setup_detection_interface(self):
        """Set up the detection interface in the right frame."""
        tk.Label(self.right_frame, text="Detection Interface", font=("Arial", 16)).pack(pady=10)

        # Video feed label for detection
        self.detection_video_label = tk.Label(self.right_frame, bg="black", text="Detection Feed")
        self.detection_video_label.pack(pady=10)

        # Logged data display
        self.csv_frame = tk.Frame(self.right_frame, bg="white", bd=2, relief="ridge")
        self.csv_frame.pack(pady=10, fill="both", expand=True)

        self.csv_label = tk.Label(self.csv_frame, text="Logged Data", font=("Arial", 14), bg="white")
        self.csv_label.pack()

        self.start_detection_feed()

    def start_operator_feed(self):
        """Start the operator video feed."""
        def update_operator_feed():
            while self.detection_running:
                frame = self.operator_camera_module.get_current_frame()
                if frame is None:
                    continue

                # Convert the frame to an image that Tkinter can display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(frame_rgb, (320, 240))
                img_tk = self.operator_camera_module.convert_to_tk_image(img)

                self.operator_video_label.config(image=img_tk)
                self.operator_video_label.image = img_tk

        threading.Thread(target=update_operator_feed, daemon=True).start()

    def start_detection_feed(self):
        """Start the detection video feed."""
        def update_detection_feed():
            while self.detection_running:
                frame = self.detection_camera_module.get_current_frame()
                if frame is None or not self.roi_coordinates:
                    continue

                # Process the frame for detection
                detected_frame = start_detection(frame, self.roi_coordinates)

                # Convert the frame to an image that Tkinter can display
                frame_rgb = cv2.cvtColor(detected_frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(frame_rgb, (320, 240))
                img_tk = self.detection_camera_module.convert_to_tk_image(img)

                self.detection_video_label.config(image=img_tk)
                self.detection_video_label.image = img_tk

        threading.Thread(target=update_detection_feed, daemon=True).start()

    def navigate_back(self):
        """Navigate back to the parent interface."""
        self.detection_running = False
        self.operator_camera_module.stop_feed()
        self.detection_camera_module.stop_feed()
        self.window.destroy()
        self.parent_interface.deiconify()

    def on_close(self):
        """Handle cleanup when the window is closed."""
        self.navigate_back()
