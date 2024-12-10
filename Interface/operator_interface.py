import tkinter as tk
import pandas as pd
import time

class OperatorInterface:
    def __init__(self, selected_process, parent_interface):
        self.window = tk.Tk()
        self.window.title('Operator Interface')
        self.parent_interface = parent_interface  # Reference to the RotatableCameraInterface

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

        # Video feed placeholder with border
        video_frame = tk.Frame(self.window, bg="black", bd=2, relief="ridge")
        video_frame.pack(pady=10)
        self.video_label = tk.Label(video_frame, text="VIDEO", font=("Arial", 14), fg="white", bg="black", width=40, height=10)
        self.video_label.pack()

        # Step display
        self.step_label = tk.Label(self.window, text="Current Step: ", font=("Arial", 14))
        self.step_label.pack(pady=10)

        # Correctness display
        self.correctness_display = tk.Text(self.window, height=10, width=50, font=("Arial", 12))
        self.correctness_display.pack(pady=10)

        # Alert display
        self.alert_label = tk.Label(self.window, text="", font=("Arial", 14), fg="red")
        self.alert_label.pack(pady=10)

        # Dummy steps for comparison
        self.dummy_steps = [
            {"horizontal_angle": 45, "vertical_angle": 45, "time": 5},  # Correct
            {"horizontal_angle": 50, "vertical_angle": 50, "time": 6},  # Incorrect
            {"horizontal_angle": 45, "vertical_angle": 45, "time": 4},  # Correct
            {"horizontal_angle": 55, "vertical_angle": 45, "time": 7},  # Incorrect
        ]

        # Start processing steps
        self.start_time = time.time()
        self.check_step()

        # Add a "Back to Supervisor Interface" button
        tk.Button(self.window, text="Back to Supervisor Interface", command=self.navigate_back).pack(pady=10)

        # Bind cleanup function to close window
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.window.mainloop()

    def check_step(self):
        if self.current_step >= len(self.steps):
            self.step_label.config(text="All steps completed!")
            self.correctness_display.insert(tk.END, f"Total Cycle Time: {self.total_time:.2f}s\n", "blue")
            self.correctness_display.tag_configure("blue", foreground="blue")
            return

        # Dummy elapsed time and angles
        elapsed_time = self.dummy_steps[self.current_step]["time"]
        dummy_horizontal_angle = self.dummy_steps[self.current_step]["horizontal_angle"]
        dummy_vertical_angle = self.dummy_steps[self.current_step]["vertical_angle"]

        # Dummy comparison function to check angles
        def compare_angles(step_h_angle, step_v_angle, dummy_h_angle, dummy_v_angle):
            horizontal_match = abs(step_h_angle - dummy_h_angle) <= 5  # Allowable difference for horizontal angle
            vertical_match = abs(step_v_angle - dummy_v_angle) <= 5  # Allowable difference for vertical angle
            return horizontal_match and vertical_match

        # Get step details from the CSV
        step_number = self.steps[self.current_step]["step_number"]
        step_h_angle = self.steps[self.current_step]["horizontal_angle"]
        step_v_angle = self.steps[self.current_step]["vertical_angle"]

        # Check correctness of the step
        if not compare_angles(step_h_angle, step_v_angle, dummy_horizontal_angle, dummy_vertical_angle):
            self.correctness_display.insert(
                tk.END,
                f"Step {step_number}: Incorrect! Angle mismatch. (H: {dummy_horizontal_angle}, V: {dummy_vertical_angle})\n",
                "red",
            )
            self.correctness_display.tag_configure("red", foreground="red")
            self.alert_label.config(text=f"ALERT: Step {step_number} incorrect!")
        else:
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
            self.alert_label.config(text="")  # Clear any remaining alert

    def navigate_back(self):
        """Navigate back to the parent interface."""
        self.window.destroy()  # Close the OperatorInterface window
        self.parent_interface.window.deiconify()  # Show the RotatableCameraInterface window

    def on_close(self):
        """Handle cleanup when the window is closed."""
        self.navigate_back()
