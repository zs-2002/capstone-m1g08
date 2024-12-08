import tkinter as tk
import cv2
from PIL import Image, ImageTk
import pandas as pd
import time

class OperatorInterface:
    def __init__(self, selected_process):
        self.window = tk.Tk()
        self.window.title('Operator Interface')

        # Load steps from supervisor based on selected process
        try:
            df = pd.read_csv("assembly_steps.csv")
            self.steps = df[df['process'] == selected_process].to_dict('records')
        except FileNotFoundError:
            tk.Label(self.window, text="Error: No Steps Defined!", fg="red").pack()
            return

        if not self.steps:
            tk.Label(self.window, text="Error: No Steps for Selected Process!", fg="red").pack()
            return

        self.current_step = 0
        self.total_time = 0  # Track total cycle time

        # Video feed display
        self.video_label = tk.Label(self.window)
        self.video_label.pack()

        # Step display
        self.step_label = tk.Label(self.window, text="Current Step: ", font=("Arial", 14))
        self.step_label.pack(pady=10)

        # Correctness display
        self.correctness_label = tk.Label(self.window, text="", font=("Arial", 14))
        self.correctness_label.pack(pady=10)

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.update_video()

        # Timer for step monitoring
        self.start_time = time.time()
        self.window.after(1000, self.check_step)

        self.window.mainloop()

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the image from OpenCV’s default BGR format to RGB, which is compatible with PIL
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert the NumPy array (frame) into a format that Tkinter can display
            img = ImageTk.PhotoImage(Image.fromarray(frame))
            self.video_label.config(image=img)
            self.video_label.image = img

        # Update the video feed every 10 milliseconds
        self.window.after(10, self.update_video)

    def check_step(self):
        elapsed_time = time.time() - self.start_time
        
        # Dummy comparison function to check angles and time
        def compare_angles(step_angle, captured_angle):
            return abs(step_angle - captured_angle) <= 5  # Example: Allowable angle difference is 5 degrees

        # Simulate angle detection (replace with actual logic for capturing angles)
        captured_angle = 45  # Dummy value for captured angle

        step_angle = self.steps[self.current_step]["angle"]
        if elapsed_time > self.steps[self.current_step]["time"]:
            if not compare_angles(step_angle, captured_angle):
                self.correctness_label.config(text="Error: Incorrect step! Angle mismatch.", fg="red")
                # Alert (sound or visual can be added here)
                print("ALERT: Incorrect step!")
                return

            # If the step is correct
            step_time = elapsed_time
            self.total_time += step_time
            self.correctness_label.config(text=f"Step {self.current_step + 1} Correct! Time: {step_time:.2f}s", fg="green")
            
            self.current_step += 1
            if self.current_step < len(self.steps):
                self.start_time = time.time()
                self.step_label.config(text=f"Current Step: {self.steps[self.current_step]['step']}")
            else:
                self.step_label.config(text="All steps completed!")
                self.correctness_label.config(text=f"Total Cycle Time: {self.total_time:.2f}s", fg="blue")
                # Stop the webcam
                self.cap.release()
                self.window.destroy()
        else:
            self.window.after(1000, self.check_step)

# Example usage:
# OperatorInterface("Manufacturing")
