import socket
import pigpio
import time

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpio daemon.")
    exit()

# GPIO Pin Setup for servos
servo_pins = {
    1: {"horizontal": 17, "vertical": 18},  # Camera 1 pins
    2: {"horizontal": 22, "vertical": 23},  # Camera 2 pins
}

# Define PWM frequency and initial position (middle)
PWM_FREQ = 50
INITIAL_POSITION = 1500  # 1500 us (middle position for most servos)

# Initialize PWM for each servo
pwm = {}
for cam_id, pins in servo_pins.items():
    pwm[cam_id] = {}
    for servo, pin in pins.items():
        pi.set_mode(pin, pigpio.OUTPUT)
        pwm[cam_id][servo] = INITIAL_POSITION
        pi.set_servo_pulsewidth(pin, INITIAL_POSITION)

def set_angle(pin, angle):
    """Convert angle to pulse width and set servo position."""
    pulsewidth = 500 + (angle / 180) * 2000  # Convert angle to pulse width (500 to 2500 us)
    pi.set_servo_pulsewidth(pin, pulsewidth)

# Network Setup
host = '0.0.0.0'
port = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print("Waiting for connections...")

try:
    while True:
        # Wait for a connection
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    print("Connection closed by client.")
                    break
                
                # Parse received data
                try:
                    cam_id, horizontal_angle, vertical_angle = map(int, data.split(","))
                    print(f"Camera {cam_id}: Horizontal Angle={horizontal_angle}, Vertical Angle={vertical_angle}")
                    
                    # Set servo angles for the specified camera
                    if cam_id in pwm:
                        set_angle(servo_pins[cam_id]["horizontal"], horizontal_angle)
                        set_angle(servo_pins[cam_id]["vertical"], vertical_angle)
                    else:
                        print(f"Invalid camera ID: {cam_id}")
                except ValueError:
                    print(f"Invalid data format: {data}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
            print("Client disconnected.")
finally:
    # Cleanup and stop servos
    for cam_id, pins in servo_pins.items():
        for pin in pins.values():
            pi.set_servo_pulsewidth(pin, 0)  # Stop the servo
    pi.stop()
    server_socket.close()
