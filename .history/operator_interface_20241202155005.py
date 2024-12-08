import tkinter as tk
import cv2
from PIL import Image, ImageTk
import pandas as pd
import time

class OperatorInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Operator Interface')
        
        # Load steps from supervisor
        try:
            self.steps = pd.read_csv("assembly_steps.csv").to.dict('records')
        except FileNotFoundError:
            tk.Label(self.window, text="Error: No Steps Defined!", fg="red").pack()
            return
        
        self.current_step = 0
        
        # Video feed display
        self.video_label = tk.Label(self.window)
        self.video_label.pack()
        
        # Step display
        self.step_label = tk.Label(self.window, text="Current Step: ", font=("Arial", 14))
        self.step_label.pack(pady=10)
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.update_video()
        
        # Timer for step monitoring
        self.start_time = time.time()
        # Schedule check_step to run every 1000 milliseconds
        self.window.after(1000, self.check_step)
        
        self.window.mainloop()
    
    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the image from OpenCV’s default BGR format to RGB, which is compatible with PIL
            frame = cv2.cvtColor(frame, cv2.COLOR.BGR2RGB)
            img
            
        