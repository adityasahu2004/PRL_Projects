import tkinter as tk
from tkinter import ttk, filedialog
import threading
import csv
import time
import random

# ========== MOCK SERIAL CLASS FOR TESTING ==========
class MockSerial:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.is_open = True

    def readline(self):
        if "COM1" in self.port or "Mock1" in self.port:
            # Simulate Temp1 and Airflow: "25.5,1.2"
            return f"{random.uniform(20, 30):.1f},{random.uniform(0.5, 2.0):.1f}\n".encode()
        elif "COM2" in self.port or "Mock2" in self.port:
            # Simulate Temp2: "26.3"
            return f"{random.uniform(20, 30):.1f}\n".encode()
        return b''

    def close(self):
        self.is_open = False

# Try to import real serial if available
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

# Serial Connection Variables
temp1_ser = None  # Serial connection for Temp1 and Airflow
temp2_ser = None  # Serial connection for Temp2
observation_count = 0  # Counter for observations
reading = False  # Flag to control reading
interval = 1  # Default time interval in seconds

def get_serial_ports():
    """Detect available serial ports and return as a list"""
    if serial:
        ports = [port.device for port in serial.tools.list_ports.comports()]
    else:
        ports = []
    return ports if ports else []

def connect_serial():
    """Connects to the selected serial ports (uses mock if needed)."""
    global temp1_ser, temp2_ser, observation_count
    port1 = port1_var.get()
    port2 = port2_var.get()
    
    try:
        if "Mock" in port1 or "Mock" in port2 or serial is None:
            temp1_ser = MockSerial(port1)
            temp2_ser = MockSerial(port2)
        else:
            temp1_ser = serial.Serial(port1, 9600, timeout=1)
            temp2_ser = serial.Serial(port2, 9600, timeout=1)
        status_label.config(text=f"Connected to {port1} & {port2}", fg="green")
        observation_count = 0
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def start_observation():
    """Starts reading serial data."""
    global reading
    if temp1_ser and temp1_ser.is_open and temp2_ser and temp2_ser.is_open:
        reading = True
        thread = threading.Thread(target=read_serial, daemon=True)
        thread.start()
        status_label.config(text="Observations Started", fg="green")

def stop_observation():
    """Stops reading serial data."""
    global reading
    reading = False
    status_label.config(text="Observations Stopped", fg="red")

def clear_observations():
    """Clears all observations from the table."""
    global observation_count
    tree.delete(*tree.get_children())
    observation_count = 0
    status_label.config(text="Observations Cleared", fg="blue")

def export_to_csv():
    """Exports table data to a CSV file."""
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Observation', 'Temp1 (°C)', 'Temp2 (°C)', 'Airflow'])
            for row in tree.get_children():
                writer.writerow(tree.item(row)['values'])
        status_label.config(text="Observations Exported to CSV", fg="green")

def read_serial():
    """Reads serial data from both ports and updates the table"""
    global temp1_ser, temp2_ser, observation_count, reading, interval
    while temp1_ser and temp1_ser.is_open and temp2_ser and temp2_ser.is_open and reading:
        try:
            temp1_line = temp1_ser.readline().decode('utf-8').strip()
            temp2_line = temp2_ser.readline().decode('utf-8').strip()
            if temp1_line and temp2_line:
                temp1_data = temp1_line.split(',')
                temp2_data = temp2_line.split(',')
                if len(temp1_data) >= 2 and len(temp2_data) >= 1:
                    observation_count += 1  # Increment observation count
                    tree.insert('', 'end', values=(observation_count, temp1_data[0], temp2_data[0], temp1_data[1]))
            time.sleep(interval)
        except:
            break

def set_interval():
    """Updates the time interval for data collection."""
    global interval
    try:
        interval = float(interval_var.get())
        status_label.config(text=f"Interval set to {interval} seconds", fg="blue")
    except ValueError:
        status_label.config(text="Invalid Interval Value", fg="red")

# GUI Setup
root = tk.Tk()
root.title("Multi-Port Observation Table")
root.geometry("900x600")
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=8, background="#000000", foreground="#ffffff", relief="flat", borderwidth=5)
style.map("TButton", background=[("active", "#333333")])
style.configure("TLabel", font=("Segoe UI", 12, "bold"))
style.configure("TCombobox", font=("Segoe UI", 12))

# Frame for Port Selection
port_frame = tk.LabelFrame(root, text="Port Selection", font=("Segoe UI", 13, "bold"), bg="#dfe6e9", bd=4)
port_frame.pack(pady=10, padx=10, fill="x")

port1_var = tk.StringVar()
port2_var = tk.StringVar()
interval_var = tk.StringVar(value="1")
ports = get_serial_ports() + ["Mock1", "Mock2"]

port1_dropdown = ttk.Combobox(port_frame, textvariable=port1_var, values=ports, state="readonly")
port1_dropdown.pack(pady=5)
port2_dropdown = ttk.Combobox(port_frame, textvariable=port2_var, values=ports, state="readonly")
port2_dropdown.pack(pady=5)

# Interval Selection Frame
interval_frame = tk.LabelFrame(root, text="Observation Interval (seconds)", font=("Segoe UI", 13, "bold"), bg="#dfe6e9", bd=4)
interval_frame.pack(pady=10, padx=10, fill="x")

interval_entry = ttk.Entry(interval_frame, textvariable=interval_var, font=("Segoe UI", 12))
interval_entry.pack(side="left", padx=5)
ttk.Button(interval_frame, text="Set Interval", command=set_interval).pack(side="left", padx=5)

# Frame for Controls
button_frame = tk.Frame(root, bg="#dfe6e9", bd=4)
button_frame.pack(pady=10, padx=10, fill="x")

buttons = [
    ("Connect", connect_serial),
    ("Start", start_observation),
    ("Stop", stop_observation),
    ("Clear", clear_observations),
    ("Export CSV", export_to_csv)
]

for text, command in buttons:
    ttk.Button(button_frame, text=text, command=command).pack(side="left", padx=5, pady=5)

# Table Frame
table_frame = ttk.Frame(root)
table_frame.pack(pady=10, padx=10, fill="both", expand=True)

columns = ('Observation', 'Temp1 (°C)', 'Temp2 (°C)', 'Airflow')
tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor="center")
tree.pack(fill="both", expand=True)

# Status Label
status_label = tk.Label(root, text="Waiting for Serial Connection...", fg="blue", font=("Segoe UI", 11, "bold"), bg="#f0f0f0")
status_label.pack(pady=5)

root.mainloop()
