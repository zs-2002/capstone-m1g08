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
        self.correctness_label = tk.Label(self.window, text="", font=("Arial", 14))
        self.correctness_label.pack(pady=10)

        # Dummy steps for comparison
        self.dummy_steps = [
            {"angle": 45, "time": 5},  # Correct
            {"angle": 50, "time": 6},  # Incorrect
            {"angle": 45, "time": 4},  # Correct
            {"angle": 55, "time": 7},  # Incorrect
        ]

        # Timer for step monitoring
        self.start_time = time.time()
        self.window.after(1000, self.check_step)

        self.window.mainloop()

    def check_step(self):
        if self.current_step >= len(self.steps):
            self.step_label.config(text="All steps completed!")
            self.correctness_label.config(text=f"Total Cycle Time: {self.total_time:.2f}s", fg="blue")
            return

        elapsed_time = self.dummy_steps[self.current_step]["time"]  # Dummy elapsed time

        # Dummy comparison function to check angles
        def compare_angles(step_angle, dummy_angle):
            return abs(step_angle - dummy_angle) <= 5  # Example: Allowable angle difference is 5 degrees

        # Simulate angle detection (replace with actual logic for capturing angles)
        dummy_angle = self.dummy_steps[self.current_step]["angle"]
        step_angle = self.steps[self.current_step]["angle"]

        if not compare_angles(step_angle, dummy_angle):
            self.correctness_label.config(text=f"Error: Incorrect step {self.current_step + 1}! Angle mismatch.", fg="red")
            print("ALERT: Incorrect step!")
        else:
            self.total_time += elapsed_time
            self.correctness_label.config(text=f"Step {self.current_step + 1} Correct! Time: {elapsed_time:.2f}s", fg="green")

        self.current_step += 1
        if self.current_step < len(self.steps):
            self.step_label.config(text=f"Current Step: {self.steps[self.current_step]['step']}")
            self.window.after(1000, self.check_step)
        else:
            self.step_label.config(text="All steps completed!")
            self.correctness_label.config(text=f"Total Cycle Time: {self.total_time:.2f}s", fg="blue")
