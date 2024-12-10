import tkinter as tk
# from tkinter import ttk
import pandas as pd
from operator_interface import OperatorInterface
from camera_module import CameraModule

class RotatableCameraInterface:
    def __init__(self):
        # Create a new Toplevel window
        self.window = tk.Toplevel()
        self.window.title("Rotatable Camera Interface")

        self.steps = []
        self.step_number = 1
        self.is_visualizing = False
        self.process_name_set = False  # Track if the process name is set initially

        # Create an instance of camera module
        self.camera_module = CameraModule()

        # Left Frame for controls
        left_frame = tk.Frame(self.window)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Video feed on the right
        self.video_label = tk.Label(self.window, bg="black")  # Keep black background
        self.video_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.video_label.grid_remove()  # Hide initially

        # Configure grid weights for resizing
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=3)  # Allocate more space for the video feed
        self.window.rowconfigure(0, weight=1)

        # Input fields
        tk.Label(left_frame, text="Process Name:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.process_name = tk.Entry(left_frame)
        self.process_name.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="w")

        tk.Label(left_frame, text="Time Required (s):").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.time_required = tk.Entry(left_frame)
        self.time_required.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="w")

        # Adjust the angle section
        tk.Label(left_frame, text="Adjust Angle:").grid(row=2, column=0, sticky="e", padx=10, pady=5)

        angle_frame = tk.Frame(left_frame)
        angle_frame.grid(row=2, column=1, columnspan=2, pady=5)

        tk.Button(angle_frame, text="Up", width=10, command=None).grid(row=0, column=1, pady=5)
        tk.Button(angle_frame, text="Left", width=10, command=None).grid(row=1, column=0, padx=5)
        tk.Button(angle_frame, text="Right", width=10, command=None).grid(row=1, column=2, padx=5)
        tk.Button(angle_frame, text="Down", width=10, command=None).grid(row=2, column=1, pady=5)

        # Visualization buttons in a labeled box
        visualization_frame = tk.LabelFrame(left_frame, text="Visualization Controls", padx=10, pady=10)
        visualization_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10)

        # Buttons inside the labeled box
        tk.Button(visualization_frame, text="Start Visualization", command=self.start_visualization).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(visualization_frame, text="Add Step", command=self.add_step).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(visualization_frame, text="Stop Visualization", command=self.stop_visualization).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(visualization_frame, text="Save Process", command=self.save_steps).grid(row=1, column=1, padx=5, pady=5)

        # Available processes
        tk.Label(left_frame, text="Available Processes:").grid(row=4, column=0, columnspan=3, padx=10, pady=5)
        self.process_list_display = tk.Text(left_frame, height=5, width=40, state='disabled')
        self.process_list_display.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

        # Current process controls
        tk.Label(left_frame, text="Type Current Process:").grid(row=6, column=0, sticky="e", padx=10, pady=5)
        self.current_process_entry = tk.Entry(left_frame)
        self.current_process_entry.grid(row=6, column=1, columnspan=1, padx=10, pady=5, sticky="w")

        tk.Button(left_frame, text="Start Current Process", command=self.start_operator_interface).grid(row=6, column=2, padx=10, pady=5)

        # Steps display
        tk.Label(left_frame, text="Steps:").grid(row=7, column=0, columnspan=3, padx=10, pady=5)
        self.step_display = tk.Text(left_frame, height=20, width=65)
        self.step_display.grid(row=8, column=0, columnspan=3, padx=10, pady=5)

    def start_visualization(self):
        # Show the video label when visualization starts
        self.video_label.grid()  # Make the video_label visible
    
        # Start the camera feed
        self.camera_module.start_feed(self.video_label)

        if not self.is_visualizing:
            process = self.process_name.get().strip()
            if not self.process_name_set:
                if process:
                    self.step_display.insert(tk.END, f"\nProcess Name: {process}\n")
                    self.process_name_set = True
                    self.process_name.config(state='disabled')  # Disable input for process name
                
                    # Reset step number for the new process
                    self.step_number = 1  
                else:
                    tk.Label(self.window, text="Please enter a process name before starting!", fg="red").grid(row=11, column=0, columnspan=2)
                    return

            self.is_visualizing = True
            print("Starting video visualization...")

    def add_step(self):
        if not self.is_visualizing:
            tk.Label(self.window, text="Start visualization before adding steps", fg="red").grid(row=11, column=0, columnspan=2)
            return

        time = self.time_required.get().strip()
        dummy_angle = 45

        if time.isdigit():
            self.steps.append({"step_number": self.step_number, "process": self.process_name.get().strip(), "angle": dummy_angle, "time": int(time)})
            self.step_display.insert(tk.END, f"Step: {self.step_number}: Horizontal angle: {dummy_angle}, Vertical Angle: {dummy_angle}, Time: {time}s\n")
            self.step_number += 1

            # Clear input fields
            self.time_required.delete(0, tk.END)
        else:
            tk.Label(self.window, text="Invalid input. Please try again!", fg="red").grid(row=11, column=0, columnspan=2)

    def stop_visualization(self):
        # Hide initially
        self.video_label.grid_remove() 
        # Stop the camera feed
        self.camera_module.stop_feed()
        self.video_label.config(image="")  # Clear the video feed

        if self.is_visualizing:
            self.is_visualizing = False
            print("Stopping video visualization...")
            self.process_name_set = False  # Allow setting a new process name after stopping
            self.process_name.config(state='normal')  # Enable input for process name
            self.process_name.delete(0, tk.END)  # Clear the process name field

    def save_steps(self):
        if not self.steps:
            tk.Label(self.window, text="No steps to save!", fg="red").grid(row=11, column=0, columnspan=2)
            return

        # Convert the steps to a DataFrame
        df = pd.DataFrame(self.steps)

        # Reset step numbering for each process
        df['step_number'] = df.groupby('process').cumcount() + 1

        # Save the DataFrame to CSV with both horizontal and vertical angles
        df = df[['process', 'step_number', 'angle', 'angle', 'time']]  # Include horizontal and vertical angles
        df.columns = ['process', 'step_number', 'horizontal_angle', 'vertical_angle', 'time']  # Rename columns

        # Save to CSV
        df.to_csv("assembly_steps.csv", index=False)

        tk.Label(self.window, text="Steps Saved!", fg="green").grid(row=11, column=0, columnspan=2)

        # List all available processes
        processes = df['process'].unique()
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
            tk.Label(self.window, text="Invalid process selected!", fg="red").grid(row=12, column=0, columnspan=2)
            return

        # Launch Operator Interface
        print(f"Launching operator interface for process: {selected_process}")
        OperatorInterface(selected_process, self)  # Pass `self` as a reference to the RotatableCameraInterface
