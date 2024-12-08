import tkinter as tk
from supervisor_interface import SupervisorInterface
from operator_interface import OperatorInterface

# Function to open supervisor interface
def open_supervisor():
    SupervisorInterface()
    
# Function to open operator interface
def open_operator():
    OperatorInterface()
 
 # Main GUI   
root = tk.Tk()
root.title("Assembly Monitoring System")

label = tk.Label(root, text="Select User Type", font=("Arial", 16))
# Pack the label with padding in the vertical direction
label.pack(pady=20)

# Button for supervisor
btn_supervisor = tk.Button(root, text="Supervisor", command=open_supervisor, width=20, height=2)
btn_supervisor.pack(pady=10)

# Button for operator
# btn_operator = tk.Button(root, text="Operator", command=open_operator, width=20, height=2)
# btn_operator.pack(pady=10)

root.mainloop()