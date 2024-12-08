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

        # Dropdown menu for current process selection
        tk.Label(self.window, text="Select Current Process:").grid(row=4, column=0)
        self.current_process_var = tk.StringVar()
        self.current_process_dropdown = ttk.Combobox(self.window, textvariable=self.current_process_var, state='readonly')
        self.current_process_dropdown.grid(row=4, column=1)
        tk.Button(self.window, text="Start Current Process", command=self.start_operator_interface).grid(row=5, column=1)

        self.step_display = tk.Text(self.window, height=10, width=60)
        self.step_display.grid(row=6, column=0, columnspan=2)

        self.window.mainloop()

    def save_steps(self):
        if not self.steps:
            tk.Label(self.window, text="No steps to save!", fg="red").grid(row=7, column=0, columnspan=2)
            return

        # Convert the steps to DataFrame
        df = pd.DataFrame(self.steps)
        df.to_csv("assembly_steps.csv", index=False)
        tk.Label(self.window, text="Steps Saved!", fg="green").grid(row=7, column=0, columnspan=2)

        # Update the dropdown menu with unique and valid process names
        processes = list(df['process'].unique())
        self.current_process_dropdown['values'] = processes
        print("Dropdown updated with processes:", processes)  # Debugging line

    def start_operator_interface(self):
        selected_process = self.current_process_var.get().strip()  # Get and trim the value
        print("Selected process:", selected_process)  # Debugging line
        if not selected_process:
            tk.Label(self.window, text="Please select a process to start!", fg="red").grid(row=8, column=0, columnspan=2)
            return

        # Ensure the selected process is valid
        valid_processes = self.current_process_dropdown['values']
        print("Dropdown values:", valid_processes)  # Debugging line
        if selected_process not in valid_processes:
            tk.Label(self.window, text="Invalid process selected!", fg="red").grid(row=8, column=0, columnspan=2)
            return

        # Launch Operator Interface
        print(f"Launching operator interface for process: {selected_process}")
        self.window.destroy()  # Close the Supervisor Interface
        OperatorInterface(selected_process)  # Open Operator Interface
