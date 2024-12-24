import tkinter as tk
import pandas as pd
import time
from check_step_cam import CameraModule
import socket
import cv2

class OperatorInterface:
    def __init__(self, selected_process, parent_interface, detection_interface=None):
        self.window = tk.Toplevel()
        self.window.title('Operator Interface')
        self.parent_interface = parent_interface  # Reference to the RotatableCameraInterface
        self.detection_interface = detection_interface  # Reference to the OpenDetectionInterface
        
        # Load steps from supervisor based on selected process
        try:
            df = pd.read_csv("assembly_steps.csv")
            self.steps = df[df['process'] == selected_process].to_dict('records')
        except FileNotFoundError:
            tk.Label(self.window, text="Error: No Steps Defined!", fg="red").grid(row=0, column=0, columnspan=2, pady=10)
            return

        if not self.steps:
            tk.Label(self.window, text="Error: No Steps for Selected Process!", fg="red").grid(row=0, column=0, columnspan=2, pady=10)
            return

        self.current_step = 0
        self.total_time = 0  # Track total cycle time
        self.step_h_angle = 90
        self.step_v_angle = 90
        self.step_time = 0

        # Initialize socket connection to RPi
        self.rpi_host = "192.168.137.121"  # Replace with your RPi's IP address
        self.rpi_port = 5000
        self.socket = None
        # self.send_angles_to_rpi()

        # Camera feed setup
        self.camera_module = CameraModule()
        self.video_label = tk.Label(self.window, bg="black")
        self.video_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Start the camera feed
        self.camera_module.start_feed(self.video_label)

        # Step display
        self.step_label = tk.Label(self.window, text="Current Step: ", font=("Arial", 14))
        self.step_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Correctness display
        self.correctness_display = tk.Text(self.window, height=10, width=50, font=("Arial", 12))
        self.correctness_display.grid(row=2, column=0, columnspan=2, pady=10)

        # Alert display
        self.alert_label = tk.Label(self.window, text="", font=("Arial", 14), fg="red")
        self.alert_label.grid(row=3, column=0, columnspan=2, pady=10)

        # Start processing steps
        self.start_time = time.time()
        self.start_step()

        # Add a "Back to Supervisor Interface" button
        tk.Button(self.window, text="Finish Process", command=self.navigate_back).grid(row=4, column=0, columnspan=2, pady=10)

        # Bind cleanup function to close window
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_step(self):
        if self.current_step >= len(self.steps):
            self.step_label.config(text="All steps completed!")
            self.correctness_display.insert(tk.END, f"Total Cycle Time: {self.total_time:.2f}s\n", "blue")
            self.correctness_display.tag_configure("blue", foreground="blue")
            return

        # Get step details from the CSV
        step_details = self.steps[self.current_step]
        self.step_h_angle = step_details["h_angle"]
        self.step_v_angle = step_details["v_angle"]
        self.step_time = step_details["time"]
        self.zoom_ratio = step_details["zoom_factor"]

        # Start asynchronous processing
        self.start_time = time.time()
        self.process_step_async()

    def process_step_async(self):
        result = self.check_step()
        if result is None:
            self.correctness_display.insert(tk.END, "Error: Angle capture function not implemented!\n", "red")
            self.correctness_display.tag_configure("red", foreground="red")
            return

        # Schedule handling the result
        self.window.after(0, self.handle_step_result, result)

    def handle_step_result(self, result):
        is_correct, elapsed_time = result

        if not is_correct:
            self.correctness_display.insert(
                tk.END,
                f"Step {self.current_step + 1}: Incorrect! Angle mismatch.\n",
                "red",
            )
            self.correctness_display.tag_configure("red", foreground="red")
            self.alert_label.config(text=f"ALERT: Step {self.current_step + 1} incorrect! Stopping process.")
            return

        # Update total time
        self.total_time += elapsed_time
        self.correctness_display.insert(
            tk.END,
            f"Step {self.current_step + 1}: Correct! Time: {elapsed_time:.2f}s\n",
            "green",
        )
        self.correctness_display.tag_configure("green", foreground="green")
        self.alert_label.config(text="")  # Clear alert

        # Move to the next step
        self.current_step += 1
        if self.current_step < len(self.steps):
            next_step_number = self.steps[self.current_step]["step_number"]
            self.step_label.config(text=f"Current Step: {next_step_number}")
            self.window.after(1000, self.start_step)
        else:
            self.step_label.config(text="All steps completed!")
            self.correctness_display.insert(tk.END, f"Total Cycle Time: {self.total_time:.2f}s\n", "blue")
            self.correctness_display.tag_configure("blue", foreground="blue")
            self.alert_label.config(text="")

    def check_step(self):
        """
        Captures angles from the camera, detects hands, and determines if the step is correct.
        Returns a tuple: (is_correct: bool, elapsed_time: float)
        """
        #self.send_angles_to_rpi()
        
        # Start the timer for hand detection
        start_time = time.time()
        hand_detected_time = 0  # Duration for which hand is detected
        detection_start = None  # Start time of continuous detection

        # Loop to monitor the hand detection
        while time.time() - start_time < self.step_time + 2:  # Allow a 2-second buffer for detection
            frame = self.camera_module.get_current_frame()  # Assuming CameraModule can provide a frame
            if frame is None:
                break

            # Convert frame to RGB for MediaPipe processing
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame for hand detection
            results = self.camera_module.mp_hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                # Hand detected
                if detection_start is None:
                    detection_start = time.time()  # Start detection timer
                else:
                    # Accumulate detection time
                    hand_detected_time += time.time() - detection_start
                    detection_start = time.time()  # Reset start time for next iteration
            else:
                detection_start = None  # Reset detection start if hand is not detected

            # Exit loop if detection time meets or exceeds required step time
            if hand_detected_time >= self.step_time:
                is_correct = True
                elapsed_time = time.time() - start_time
                return is_correct, elapsed_time

        # If loop exits without sufficient hand detection time
        is_correct = False
        elapsed_time = time.time() - start_time
        return is_correct, elapsed_time

    
    # def send_angles_to_rpi(self):
    #     try:
    #         if self.socket is None:
    #             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             self.socket.connect((self.rpi_host, self.rpi_port))

    #         data = f"{1},{self.step_h_angle},{self.step_h_angle}" # 1 for cam1
    #         self.socket.sendall(data.encode('utf-8'))
    #         print(f"Sent angles to RPi: {data}")
    #     except Exception as e:
    #         print(f"Error sending angles to RPi: {e}")
    #         self.socket = None  # Reset the socket if an error occurs

    def navigate_back(self):
        """Navigate back to the parent interface."""
        self.camera_module.stop_feed()
        if self.detection_interface:
            self.detection_interface.stop_detection()  # Stop detection before navigating back
        self.window.destroy()
        self.parent_interface.window.deiconify()

    def on_close(self):
        """Handle cleanup when the window is closed."""
        self.navigate_back()
