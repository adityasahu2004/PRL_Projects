import sys
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, scrolledtext

class StepperMotorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stepper Motor Control")
        self.root.geometry("400x400")
        
        self.arduino = None
        
        self.port_label = tk.Label(root, text="Select Port:")
        self.port_label.pack()
        
        self.port_combo = ttk.Combobox(root)
        self.refresh_ports()
        self.port_combo.pack()
        
        self.connect_button = tk.Button(root, text="Connect", command=self.connect_arduino)
        self.connect_button.pack()
        
        self.disconnect_button = tk.Button(root, text="Disconnect", command=self.disconnect_arduino)
        self.disconnect_button.pack()
        
        self.steps_label = tk.Label(root, text="Enter Steps:")
        self.steps_label.pack()
        
        self.steps_entry = tk.Entry(root)
        self.steps_entry.pack()
        
        self.move_button = tk.Button(root, text="Move", command=self.move_motor)
        self.move_button.pack()
        
        self.output_text = scrolledtext.ScrolledText(root, height=8, width=50, state='disabled')
        self.output_text.pack()
        
    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combo['values'] = [port.device for port in ports]
        if ports:
            self.port_combo.current(0)
    
    def connect_arduino(self):
        selected_port = self.port_combo.get()
        try:
            self.arduino = serial.Serial(selected_port, 9600, timeout=1)
            self.append_output(f"Connected to {selected_port}")
        except Exception as e:
            self.append_output(f"Error: {e}")
    
    def disconnect_arduino(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            self.append_output("Disconnected from Arduino")
        else:
            self.append_output("Error: No active connection")
    
    def move_motor(self):
        steps = self.steps_entry.get()
        if steps.isdigit() or (steps.startswith('-') and steps[1:].isdigit()):
            command = f's{steps}'
            self.send_command(command)
        else:
            self.append_output("Error: Enter a valid step count")
    
    def send_command(self, command):
        if self.arduino and self.arduino.is_open:
            self.arduino.reset_input_buffer()  # Clear any previous data
            self.arduino.write(command.encode())
            self.arduino.flush()
            response = self.arduino.readline().decode().strip()
            if response:
                self.append_output(f"Arduino: {response}")
        else:
            self.append_output("Error: Not connected to Arduino")
    
    def append_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text + '\n')
        self.output_text.config(state='disabled')
        self.output_text.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = StepperMotorUI(root)
    root.mainloop()

