import tkinter as tk
from tkinter import ttk
import pandas as pd

class SupervisorInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Supervisor Interface")
        
        self.steps = []
        self.step_number = 1
        self.is_visualizing = False
        self.process_name_set = False # Track if the step name is set initially 
        
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
    
    def start_visualization(self):
        if not self.is_visualizing:
            if not self.process_name_set:
                process = self.process_name.get()
                if process:
                    self.step_display.insert(tk.END, f"\nProcess Name: {process}\n")
                    self.process_name_set = True
                    self.process_name.config(state='disabled')  # Disable input for process name
                else:
                    tk.Label(self.window, text="Please enter a process name before starting!", fg="red").grid(row=7, column=0, columnspan=2)
                    return

            self.is_visualizing = True
            print("Starting video visualization...")    
            
    def add_step(self):
        if not self.is_visualizing:
            tk.Label(self.window, text="Start visualization before adding steps", fg="red").grid(row=7, column=0, columnspan=2)
            return
         
        time = self.time_required.get()
        dummy_angle = 45
        
        if time.isdigit():
            self.steps.append({"step_number": self.step_number, "process": self.process_name.get(), "angle": dummy_angle, "time": int(time)})
            self.step_display.insert(tk.END, f"Step: {self.step_number}: Angle: {dummy_angle}, Time: {time}s\n")
            self.step_number += 1
            
            # Clear input fields
            self.time_required.delete(0, tk.END)
        else:
            tk.Label(self.window, text="Invalid input. Please try again!", fg="red").grid(row=7, column=0, columnspan=2)
            
    def stop_visualization(self):
        if self.is_visualizing:
            self.is_visualizing = False
            print("Stopping video visualization...")
            self.process_name_set = False  # Allow setting a new process name after stopping
            self.process_name.config(state='normal')  # Enable input for process name
            self.process_name.delete(0, tk.END)  # Clear the process name field
        else:
            tk.Label(self.window, text="Visualization is not running!", fg="red").grid(row=7, column=0, columnspan=2) 
    
    def save_steps(self):
        if not self.steps:
            tk.Label(self.window, text="No steps to save!", fg="red").grid(row=7, column=0, columnspan=2)
            return
        
        # Convert the steps to dataframe
        df = pd.DataFrame(self.steps)
        df.to_csv("assembly_steps.csv", index=False)
        tk.Label(self.window, text="Steps Saved!", fg="green").grid(row=7, column=0, columnspan=2)
        
        # Update the dropdown menu with process names
        processes = list(df['process'].unique())  # Convert to a list of unique process names
        self.current_process_dropdown['values'] = processes
                
    def start_operator_interface(self):
        selected_process = self.current_process_var.get()
        if not selected_process:
            tk.Label(self.window, text="Please select a process to start!", fg="red").grid(row=8, column=0, columnspan=2)
            return
        
        # Placeholder for launching operator interface
        print(f"Launching operator interface for process: {selected_process}")
        self.step_display.insert(tk.END, f"\nOperator Interface started for process: {selected_process}\n")
