from ultralytics import YOLO
import cv2
import math
import time
from datetime import datetime
import pandas as pd
from roi_selector import select_roi  # Import the ROI selection function

# Initialize the camera and YOLO model
cap = cv2.VideoCapture(0)
model = YOLO("models/weights/best.pt")

# Set camera resolution to 1920x1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Define class names
classNames = ["backpack", "bench", "handbag", "person", "refrigerator", "product"]

# Use the ROI selector to define the region of interest
roi_x1, roi_y1, roi_x2, roi_y2 = select_roi(camera_index=0, resolution=(1920, 1080))

# Ensure valid ROI selection
if None in (roi_x1, roi_y1, roi_x2, roi_y2):
    print("No valid ROI selected. Exiting...")
    cap.release()
    cv2.destroyAllWindows()
    exit()

# Tracking objects
tracked_objects = {}
class_counters = {"person": 1, "product": 1}  # Separate counters for each class
buffer_time = 1  # Buffer for maintaining stability
iou_threshold = 0.2  # Minimum IoU for considering as the same object
distance_threshold = 150  # Euclidean distance threshold
min_duration = 10  # Minimum duration (in seconds) for logging

# Data logging
logged_data = []

# Helper function to calculate IoU
def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture frame. Exiting...")
        break

    results = model(img, stream=True, conf=0.7)

    # Draw the ROI rectangle on the frame
    cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)  # Green ROI border

    # Temporary storage for currently detected objects
    detected_objects = []

    for r in results:
        boxes = r.boxes

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            class_name = classNames[class_id]

            # Detect "person" everywhere
            if class_name == "person":
                detected_objects.append({'bbox': (x1, y1, x2, y2), 'class_name': class_name})

            # Detect "product" only inside the ROI
            elif class_name == "product":
                if x1 >= roi_x1 and y1 >= roi_y1 and x2 <= roi_x2 and y2 <= roi_y2:
                    detected_objects.append({'bbox': (x1, y1, x2, y2), 'class_name': class_name})

    # Match detected objects with tracked objects
    current_time = time.time()
    new_tracked_objects = {}

    for detected in detected_objects:
        bbox = detected['bbox']
        class_name = detected['class_name']

        # Assign a unique ID to new objects or match with existing ones
        best_match_id = None
        best_iou = 0
        best_distance = float('inf')

        for obj_id, tracked in tracked_objects.items():
            if tracked['class_name'] != class_name:
                continue  # Only compare objects of the same class

            tracked_bbox = tracked['bbox']
            detected_center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
            tracked_center = ((tracked_bbox[0] + tracked_bbox[2]) / 2, (tracked_bbox[1] + tracked_bbox[3]) / 2)

            # Calculate IoU and distance
            iou = calculate_iou(bbox, tracked_bbox)
            distance = math.sqrt((detected_center[0] - tracked_center[0])**2 +
                                 (detected_center[1] - tracked_center[1])**2)

            # Use both IoU and distance for matching
            if iou > best_iou and distance < distance_threshold:
                best_iou = iou
                best_distance = distance
                best_match_id = obj_id

        if best_match_id is not None:
            # Update existing tracked object
            new_tracked_objects[best_match_id] = {
                'bbox': bbox,
                'start_time': tracked_objects[best_match_id]['start_time'],
                'last_seen': current_time,
                'class_name': class_name
            }
        else:
            # Create a new tracked object with a class-specific ID
            object_id = class_counters[class_name]
            class_counters[class_name] += 1  # Increment the counter for this class

            new_tracked_objects[object_id] = {
                'bbox': bbox,
                'start_time': current_time,
                'last_seen': current_time,
                'class_name': class_name
            }

    # Retain objects within the buffer time
    for obj_id, tracked in tracked_objects.items():
        if obj_id not in new_tracked_objects:
            if current_time - tracked['last_seen'] <= buffer_time:
                new_tracked_objects[obj_id] = tracked
            else:
                # Object left the ROI; log data if duration exceeds minimum
                elapsed_time = tracked['last_seen'] - tracked['start_time']
                if elapsed_time >= min_duration:
                    logged_data.append({
                        'ID': obj_id,
                        'Class': tracked['class_name'],
                        'Start Time': datetime.fromtimestamp(tracked['start_time']).strftime('%I:%M:%S %p'),
                        'End Time': datetime.fromtimestamp(tracked['last_seen']).strftime('%I:%M:%S %p'),
                        'Total Duration (s)': round(elapsed_time, 2)
                    })

    # Update tracked objects
    tracked_objects = new_tracked_objects

    # Draw bounding boxes and labels
    for obj_id, tracked in tracked_objects.items():
        bbox = tracked['bbox']
        elapsed_time = current_time - tracked['start_time']

        # Draw bounding box and label
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 255), 3)
        cv2.putText(img, f"{tracked['class_name']} {obj_id}: {elapsed_time:.2f}s",
                    (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow('Webcam', img)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Save logged data to a CSV
df = pd.DataFrame(logged_data)
df.to_csv("Time_data.csv", index=False)
print("ROI data saved to Time_data.csv")
