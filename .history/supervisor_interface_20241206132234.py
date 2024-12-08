import tkinter as tk
import pandas as pd

class SupervisorInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Supervisor Interface")
        
        self.steps = []
        self.step_number = 1
        self.is_visualizing = False
        
        # Input fields
        tk.Label(self.window, text="Step Name:").grid(row=0, column=0)
        self.step_name = tk.Entry(self.window)
        self.step_name.grid(row=0, column=1)
        
        tk.Label(self.window, text="Time Required (s):").grid(row=1, column=0)
        self.time_required = tk.Entry(self.window)
        self.time_required.grid(row=1, column=1)
        
        # Buttons
        tk.Button(self.window, text="Start", command=self.start_visualization).grid(row=2, column=0)
        tk.Button(self.window, text="Add Step", command=self.add_step).grid(row=2, column=1)
        tk.Button(self.window, text="Stop", command=self.stop_visualization).grid(row=3, column=0)
        tk.Button(self.window, text="Save Steps", command=self.save_steps).grid(row=3, column=1)
        
        self.step_display = tk.Text(self.window, height=10, width=60)
        self.step_display.grid(rows=3, column=0, columnspan=2)
        
        self.window.mainloop()
    
    
    def start_visualization(self):
        if not self.is_visualizing:
            self.is_visualizing = True
            print("Starting video visualization...")    
            
    def add_step(self):
        if not self.is_visualizing:
            tk.Label(self.window, text="Start visualization before adding steps", fg="red").grid(row=5, column=0, columnspan=2)
            return
         
        step = self.step_name.get()
        time = self.time_required.get()
        dummy_angle = 45
        
        if step and time.isdigit():
            self.steps.append({"step_number": self.step_number, "step": step, "angle": dummy_angle, "time": int(time)})
            self.step_display.insert(tk.END, f"Step: {self.step_number}: {step}, Angle: {dummy_angle}, Time: {time}s\n")
            self.step_number += 1
            
            # Clear input fields
            self.step_name.delete(0, tk.END)
            self.time_required.delete(0, tk.END)
        else:
            tk.Label(self.window, text="Invalid input. Please try again!", fg="red").grid(row=5, column=0, columnspan=2)
            
    def stop_visualization(self):
        if self.is_visualizing:
            self.is_visualizing = False
            print("STopping video visualization...")
        else:
            tk.Label(self.window, text="Visualizing is not running!", fg="red").grid(row=5, column=0, columnspan=2) 
    
    def save_steps(self):
        if not self.steps:
            tk.Label(self.window, text="No steps to save!", fg="red").grid(row=5, column=0, columnspan=2)
            return
        
        # Convert the steps to dataframe
        df = pd.DataFrame(self.steps)
        df.to_csv("assembly_steps.csv", index=False)
        tk.Label(self.window, text="steps Saved!", fg="green").grid(row=5, column=0, columnspan=2)
                