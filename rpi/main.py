import socket
import RPi.GPIO as GPIO
import time

# GPIO Pin Setup
GPIO.setmode(GPIO.BCM)

# Define servo pins for Camera 1 and Camera 2
servo_pins = {
    1: {"horizontal": 17, "vertical": 18},  # Camera 1 pins
    2: {"horizontal": 22, "vertical": 23},  # Camera 2 pins
}

# Initialize PWM for each servo
pwm = {}
for cam_id, pins in servo_pins.items():
    pwm[cam_id] = {}
    for servo, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT)
        pwm[cam_id][servo] = GPIO.PWM(pin, 50)  # 50 Hz PWM frequency
        pwm[cam_id][servo].start(7.5)  # Initialize at the middle position

def set_angle(servo_pwm, angle):
    """Convert angle to duty cycle and set servo position."""
    duty_cycle = 2.5 + (angle / 180) * 10
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.1)

# Network Setup
host = '0.0.0.0'
port = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print("Waiting for connection...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

try:
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        
        # Parse received data
        try:
            cam_id, horizontal_angle, vertical_angle = map(int, data.split(","))
            print(f"Camera {cam_id}: Horizontal Angle={horizontal_angle}, Vertical Angle={vertical_angle}")
            
            # Set servo angles for the specified camera
            if cam_id in pwm:
                set_angle(pwm[cam_id]["horizontal"], horizontal_angle)
                set_angle(pwm[cam_id]["vertical"], vertical_angle)
            else:
                print(f"Invalid camera ID: {cam_id}")
        except ValueError:
            print(f"Invalid data format: {data}")

finally:
    for cam_id, servos in pwm.items():
        for servo_pwm in servos.values():
            servo_pwm.stop()
    GPIO.cleanup()
    conn.close()
