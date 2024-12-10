import tkinter as tk
from rotatable_camera import RotatableCameraInterface
from wide_angle_camera import WideAngleCameraInterface

# Function to open wide-angle camera interface
def open_wide_camera():
    WideAngleCameraInterface()

# Function to open rotatable camera interface
def open_rotatable_camera():
    RotatableCameraInterface()

# Main GUI
root = tk.Tk()
root.title("Assembly Monitoring System")

label = tk.Label(root, text="Select The Camera", font=("Arial", 16))
label.pack(pady=20)

# Button for wide-angle camera
btn_wide_camera = tk.Button(root, text="Wide-Angle Camera", command=open_wide_camera, width=20, height=2)
btn_wide_camera.pack(pady=10)

# Button for rotatable camera 1
btn_rotatable1 = tk.Button(root, text="Rotatable Camera 1", command=open_rotatable_camera, width=20, height=2)
btn_rotatable1.pack(pady=10)

# Button for rotatable camera 2
btn_rotatable2 = tk.Button(root, text="Rotatable Camera 2", command=open_rotatable_camera, width=20, height=2)
btn_rotatable2.pack(pady=10)

root.mainloop()
