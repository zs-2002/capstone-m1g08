import tkinter as tk
from tkinter import ttk
import pandas as pd
from operator_interface import OperatorInterface

class SupervisorInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Supervisor Interface")

        self.steps = []
        self.step_number = 1
        self.is_visualizing = False
        self.process_name_set = False  # Track if the process name is set initially

        # Input fields
        tk.Label(self.window, text="Process Name:").grid(row=0, column=0)
        self.process_name = tk.Entry(self.window)
        self.process_name.grid(row=0, column=1)

        tk.Label(self.window, text="Time Required (s):").grid(row=1, column=0)
        self.time_required = tk.Entry(self.window)
        self.time_required.grid(row=1, column=1)

        # Buttons
        tk.Button(self.window, text="Start Visualization", command=self.start_visualization).grid(row=2, column=0)
        tk.Button(self.window, text="Add Step", command=self.add_step).grid(row=2, column=1)
        tk.Button(self.window, text="Stop Visualization", command=self.stop_visualization).grid(row=3, column=0)
        tk.Button(self.window, text="Save Steps", command=self.save_steps).grid(row=3, column=1)

        # List processes and allow user to type a process
        tk.Label(self.window, text="Available Processes:").grid(row=4, column=0, columnspan=2)
        self.process_list_display = tk.Text(self.window, height=5, width=60, state='disabled')
        self.process_list_display.grid(row=5, column=0, columnspan=2)

        tk.Label(self.window, text="Type Current Process:").grid(row=6, column=0)
        self.current_process_entry = tk.Entry(self.window)
        self.current_process_entry.grid(row=6, column=1)

        tk.Button(self.window, text="Start Current Process", command=self.start_operator_interface).grid(row=7, column=1)

        self.step_display = tk.Text(self.window, height=10, width=60)
        self.step_display.grid(row=8, column=0, columnspan=2)

        self.window.mainloop()

    def start_visualization(self):
        if not self.is_visualizing:
            if not self.process_name_set:
                process = self.process_name.get().strip()
                if process:
                    self.step_display.insert(tk.END, f"\nProcess Name: {process}\n")
                    self.process_name_set = True
                    self.process_name.config(state='disabled')  # Disable input for process name
                else:
                    tk.Label(self.window, text="Please enter a process name before starting!", fg="red").grid(row=9, column=0, columnspan=2)
                    return

            self.is_visualizing = True
            print("Starting video visualization...")

    def add_step(self):
        if not self.is_visualizing:
            tk.Label(self.window, text="Start visualization before adding steps", fg="red").grid(row=9, column=0, columnspan=2)
            return

        time = self.time_required.get().strip()
        dummy_angle = 45

        if time.isdigit():
            self.steps.append({"step_number": self.step_number, "process": self.process_name.get().strip(), "angle": dummy_angle, "time": int(time)})
            self.step_display.insert(tk.END, f"Step: {self.step_number}: Angle: {dummy_angle}, Time: {time}s\n")
            self.step_number += 1

            # Clear input fields
            self.time_required.delete(0, tk.END)
        else:
            tk.Label(self.window, text="Invalid input. Please try again!", fg="red").grid(row=9, column=0, columnspan=2)

    def stop_visualization(self):
        if self.is_visualizing:
            self.is_visualizing = False
            print("Stopping video visualization...")
            self.process_name_set = False  # Allow setting a new process name after stopping
            self.process_name.config(state='normal')  # Enable input for process name
            self.process_name.delete(0, tk.END)  # Clear the process name field
        else:
            tk.Label(self.window, text="Visualization is not running!", fg="red").grid(row=9, column=0, columnspan=2)

    def save_steps(self):
        if not self.steps:
            tk.Label(self.window, text="No steps to save!", fg="red").grid(row=9, column=0, columnspan=2)
            return

        # Convert the steps to DataFrame
        df = pd.DataFrame(self.steps)
        df.to_csv("assembly_steps.csv", index=False)
        tk.Label(self.window, text="Steps Saved!", fg="green").grid(row=9, column=0, columnspan=2)

        # List all available processes
        processes = list(df['process'].unique())
        self.process_list_display.config(state='normal')
        self.process_list_display.delete(1.0, tk.END)
        self.process_list_display.insert(tk.END, "\n".join(processes))
        self.process_list_display.config(state='disabled')
        print("Available processes:", processes)  # Debugging line

    def start_operator_interface(self):
        selected_process = self.current_process_entry.get().strip()
        print("Typed process in start_operator_interface:", selected_process)  # Debugging line

        # Ensure the selected process exists in saved processes
        df = pd.read_csv("assembly_steps.csv")
        available_processes = df['process'].unique()
        print("Available processes:", available_processes)  # Debugging line

        if selected_process not in available_processes:
            tk.Label(self.window, text="Invalid process selected!", fg="red").grid(row=10, column=0, columnspan=2)
            return

        # Launch Operator Interface
        print(f"Launching operator interface for process: {selected_process}")
        self.window.destroy()  # Close the Supervisor Interface
        OperatorInterface(selected_process)  # Open Operator Interface
