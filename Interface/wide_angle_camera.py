import tkinter as tk
from tkinter import messagebox, ttk
from roi_selector import select_roi
from detection_script import start_detection
import threading
import pandas as pd


class WideAngleCameraInterface:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Wide-Angle Camera Interface")

        # Initialize attributes
        self.roi_coordinates = None
        self.detection_running = False
        self.stop_event = threading.Event()  # Event to signal stopping the detection thread
        self.logged_data = []  # Initialize logged data

        # Create video feed frame
        self.video_frame = tk.Frame(self.window, bg="black", bd=2, relief="ridge")
        self.video_frame.pack(pady=10)
        self.video_label = tk.Label(self.video_frame, text="Video Feed", font=("Arial", 14), fg="white", bg="black")
        self.video_label.pack()

        # Button frame
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(pady=10, fill="x")

        # ROI selection button
        self.roi_button = tk.Button(self.button_frame, text="Select ROI", command=self.select_roi)
        self.roi_button.pack(side="left", padx=10)

        # Start and stop detection buttons
        self.start_detection_button = tk.Button(self.button_frame, text="Start Detection", command=self.start_detection)
        self.start_detection_button.pack(side="left", padx=10)
        self.stop_detection_button = tk.Button(self.button_frame, text="Stop Detection", command=self.stop_detection, state="disabled")
        self.stop_detection_button.pack(side="left", padx=10)

        # CSV display frame
        self.csv_frame = tk.Frame(self.window, bg="white", bd=2, relief="ridge")
        self.csv_frame.pack(pady=10, fill="both", expand=True)

        self.csv_label = tk.Label(self.csv_frame, text="Logged Data", font=("Arial", 14), bg="white")
        self.csv_label.pack()

        # Add an Update button below the CSV display frame
        self.update_button = tk.Button(self.window, text="Update Data", command=self.update_csv_data)
        self.update_button.pack(pady=10)

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_roi(self):
        self.roi_coordinates = select_roi(camera_index=0, resolution=(1280, 720))
        if self.roi_coordinates and None not in self.roi_coordinates:
            messagebox.showinfo("ROI Selection", f"ROI selected: {self.roi_coordinates}")
        else:
            messagebox.showerror("ROI Selection", "No valid ROI selected.")

    def start_detection(self):
        if not self.roi_coordinates or None in self.roi_coordinates:
            messagebox.showerror("Start Detection", "Please select a valid ROI first.")
            return

        self.detection_running = True
        self.stop_event.clear()  # Clear the stop signal
        self.start_detection_button.config(state="disabled")
        self.stop_detection_button.config(state="normal")

        self.detection_thread = threading.Thread(
            target=self.run_detection,
            args=(),
            daemon=True
        )
        self.detection_thread.start()

    def run_detection(self):
        try:
            # Run the detection and log data
            start_detection(self.roi_coordinates, self.video_label, self.stop_event)

            # Example: Add dummy logged data (replace with actual detection data)
            self.logged_data.append({
                "ID": 1,
                "Class": "person",
                "Start Time": "02:34:02 PM",
                "End Time": "02:34:14 PM",
                "Total Duration (s)": 12.72,
            })

        except tk.TclError as e:
            print(f"Widget error during detection: {e}")
        finally:
            # Ensure GUI resets after the detection thread finishes
            self.reset_video_feed()

    def stop_detection(self):
        """Stop detection and reset the video feed display."""
        if self.detection_running:
            self.detection_running = False
            self.stop_event.set()  # Signal the thread to stop
            self.start_detection_button.config(state="normal")
            self.stop_detection_button.config(state="disabled")
            self.reset_video_feed()

            # Save the logged data to the CSV file
            if self.logged_data:
                df = pd.DataFrame(self.logged_data)
                df.to_csv("time_data.csv", index=False)
                print("Logged data saved.")
            else:
                print("No data to save.")

            # Reload the CSV data into the GUI
            self.display_csv_data("time_data.csv")

            # Force the GUI to refresh
            self.csv_frame.update_idletasks()

    def reset_video_feed(self):
        """Reset the video label to display 'Video Feed' text."""
        if self.video_label.winfo_exists():
            self.video_label.config(
                image='',  # Clear the image
                text="Video Feed",  # Reset to default text
                bg="black",  # Background color
                fg="white",  # Text color
                font=("Arial", 14)  # Font style
            )

    def display_csv_data(self, file_path):
        """
        Reads a CSV file and displays its contents in a Treeview widget.
        :param file_path: Path to the CSV file to display.
        """
        # Clear the CSV frame before adding new content
        for widget in self.csv_frame.winfo_children():
            widget.destroy()

        try:
            # Load the CSV data
            data = pd.read_csv(file_path)

            # Create the Treeview widget
            tree = ttk.Treeview(self.csv_frame, columns=list(data.columns), show="headings")
            tree.pack(fill="both", expand=True)

            # Configure column headers
            for col in data.columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=120)  # Adjust column width

            # Insert rows into the Treeview
            for _, row in data.iterrows():
                tree.insert("", "end", values=list(row))

        except FileNotFoundError:
            tk.Label(self.csv_frame, text="No data file found.", font=("Arial", 12), fg="red").pack()
        except Exception as e:
            tk.Label(self.csv_frame, text=f"Error loading data: {e}", font=("Arial", 12), fg="red").pack()

    def update_csv_data(self):
        """Reload the CSV data into the Treeview."""
        try:
            self.display_csv_data("time_data.csv")
            print("CSV data updated.")
        except Exception as e:
            messagebox.showerror("Update Error", f"Could not update CSV data: {e}")

    def on_closing(self):
        self.stop_detection()
        self.window.destroy()
