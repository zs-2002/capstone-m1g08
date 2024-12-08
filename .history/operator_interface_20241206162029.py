import tkinter as tk
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
            {"angle": 45, "time": 5},  # Correct
            {"angle": 50, "time": 6},  # Incorrect
            {"angle": 45, "time": 4},  # Correct
            {"angle": 55, "time": 7},  # Incorrect
        ]

        # Start processing steps
        self.start_time = time.time()
        self.check_step()

        self.window.mainloop()

    def check_step(self):
        if self.current_step >= len(self.steps):
            self.step_label.config(text="All steps completed!")
            self.correctness_display.insert(tk.END, f"Total Cycle Time: {self.total_time:.2f}s\n", "blue")
            self.correctness_display.tag_configure("blue", foreground="blue")
            return

        # Dummy elapsed time and angle
        elapsed_time = self.dummy_steps[self.current_step]["time"]
        dummy_angle = self.dummy_steps[self.current_step]["angle"]

        # Dummy comparison function to check angles
        def compare_angles(step_angle, dummy_angle):
            return abs(step_angle - dummy_angle) <= 5  # Example: Allowable angle difference is 5 degrees

        # Get step details from the CSV
        step_number = self.steps[self.current_step]["step_number"]
        step_angle = self.steps[self.current_step]["angle"]

        # Check correctness of the step
        if not compare_angles(step_angle, dummy_angle):
            self.correctness_display.insert(tk.END, f"Step {step_number}: Incorrect! Angle mismatch.\n", "red")
            self.correctness_display.tag_configure("red", foreground="red")
            self.alert_label.config(text=f"ALERT: Step {step_number} incorrect!")
        else:
            self.total_time += elapsed_time
            self.correctness_display.insert(tk.END, f"Step {step_number}: Correct! Time: {elapsed_time:.2f}s\n", "green")
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
