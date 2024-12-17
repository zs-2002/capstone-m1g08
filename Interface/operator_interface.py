import tkinter as tk
import pandas as pd
import time
from camera_module import CameraModule

class OperatorInterface:
    def __init__(self, selected_process, parent_interface):
        self.window = tk.Toplevel()
        self.window.title('Operator Interface')
        self.parent_interface = parent_interface  # Reference to the RotatableCameraInterface

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
        self.check_step()

        # Add a "Back to Supervisor Interface" button
        tk.Button(self.window, text="Back to Supervisor Interface", command=self.navigate_back).grid(row=4, column=0, columnspan=2, pady=10)

        # Bind cleanup function to close window
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def capture_and_compare_angles(self, step_h_angle, step_v_angle):
        """
        Placeholder for a function that captures angles from the camera, compares them with step values,
        and returns a tuple: (is_correct: bool, elapsed_time: float)
        """
        # TO BE IMPLEMENTED BY ZHI SHENG
        # This function should:
        # 1. Capture the angles from the camera.
        # 2. Compare captured angles with step_h_angle and step_v_angle.
        # 3. Calculate the time taken for the step.
        # 4. Return True (if angles match) or False (if angles do not match) along with elapsed time.
        pass

    def check_step(self):
        if self.current_step >= len(self.steps):
            self.step_label.config(text="All steps completed!")
            self.correctness_display.insert(tk.END, f"Total Cycle Time: {self.total_time:.2f}s\n", "blue")
            self.correctness_display.tag_configure("blue", foreground="blue")
            return

        # Get step details from the CSV
        step_number = self.steps[self.current_step]["step_number"]
        step_h_angle = self.steps[self.current_step]["horizontal_angle"]
        step_v_angle = self.steps[self.current_step]["vertical_angle"]

        # Call the placeholder function
        result = self.capture_and_compare_angles(step_h_angle, step_v_angle)

        if result is None:
            self.correctness_display.insert(tk.END, "Error: Angle capture function not implemented!\n", "red")
            self.correctness_display.tag_configure("red", foreground="red")
            return

        # Unpack the tuple
        is_correct, elapsed_time = result
        
        if not is_correct:
            # Display error and stop iteration
            self.correctness_display.insert(
                tk.END,
                f"Step {step_number}: Incorrect! Angle mismatch.\n",
                "red",
            )
            self.correctness_display.tag_configure("red", foreground="red")
            self.alert_label.config(text=f"ALERT: Step {step_number} incorrect! Stopping process.")
            return  # Stop further steps

        # Update total time
        self.total_time += elapsed_time
        self.correctness_display.insert(
            tk.END,
            f"Step {step_number}: Correct! Time: {elapsed_time:.2f}s\n",
            "green",
        )
        self.correctness_display.tag_configure("green", foreground="green")
        self.alert_label.config(text="")  # Clear alert

        # Move to the next step
        self.current_step += 1
        if self.current_step < len(self.steps):
            next_step_number = self.steps[self.current_step]["step_number"]
            self.step_label.config(text=f"Current Step: {next_step_number}")
            self.window.after(1000, self.check_step)
        else:
            self.step_label.config(text="All steps completed!")
            self.correctness_display.insert(tk.END, f"Total Cycle Time: {self.total_time:.2f}s\n", "blue")
            self.correctness_display.tag_configure("blue", foreground="blue")
            self.alert_label.config(text="")

    def navigate_back(self):
        """Navigate back to the parent interface."""
        self.camera_module.stop_feed()
        self.window.destroy()
        self.parent_interface.window.deiconify()

    def on_close(self):
        """Handle cleanup when the window is closed."""
        self.navigate_back()
