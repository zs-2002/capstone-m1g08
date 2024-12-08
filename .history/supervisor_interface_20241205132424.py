import tkinter as tk
import pandas as pd

class SupervisorInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Supervisor Interface")
        
        self.steps = []
        
        # Input fields
        tk.Label(self.window, text="Step Name:").grid(row=0, column=0)
        self.step_name = tk.Entry(self.window)
        self.step_name.grid(row=0, column=1)
        
        tk.Label(self.window, text="Time Required (s):").grid(row=1, column=0)
        self.time_required = tk.Entry(self.window)
        self.time_required.grid(row=1, column=1)
        
        # Buttons
        tk.Button(self.window, text="Add Step", command=self.add_step).grid(row=2, column=0)
        tk.Button(self.window, text="Save Steps", command=self.save_steps).grid(row=2, column=1)
        
        self.step_display = tk.Text(self.window, height=10, width=40)
        self.step_display.grid(rows=3, column=0, columnspan=2)
        
        self.window.mainloop()
        
        def add_step(self):
            step = self.step_name.get()
            time = self.time_required.get()
            if step and time.isdigit():
                self.steps.append({"step": step, "time": int(time)})
                self.step_display.insert(tk.END, f"Step: {step}, Time: {time}s\n")
                self.step_name.delete(0, tk.END)
                self.time_required.delete(0, tk.END)
        
        def save_steps(self):
            # Convert the steps to dataframe
            df = pd.DataFrame(self.steps)
            df.to_csv("assembly_steps.csv", index=False)
            tk.Label(self.window, text="steps Saved!", fg="green").grid(row=4, column=0, columnspan=2)
                