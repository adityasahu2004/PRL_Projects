# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 18:26:08 2022

@author: Bob
"""

import sys
import numpy as np
import socket
import csv
import pandas as pd
import os
import time
from tkinter import Tk, Label, Button
from threading import Thread

#functions used 
# Label which shows message  i.e. Waiting to start client 
def update_status(message, color="black"):
    """Update the status message on the GUI."""
    status_label.config(text=message, fg=color)
    root.update()
    
# Update Qber in GUI
def update_qber(qber):
    """Update the QBER on the GUI."""
    qber_label.config(text=f"QBER: {qber * 100:.2f}%", fg="green")
    root.update()

#Update Keylength in GUI
def update_key_length(key_length):
    """Update the Key Length on the GUI."""
    key_length_label.config(text=f"Key Length: {key_length}", fg="green")
    root.update()
    
# Function to Start Client
def start_client():
    """Start the client in a separate thread."""
    global client_running
    client_running = True
    start_button.config(state="disabled", bg="green", text="Client Running")
    stop_button.config(state="normal")
    Thread(target=run_client, daemon=True).start()

# Function to stop client 
def stop_client():
    """Stop the client and update the GUI."""
    global client_running
    client_running = False
    start_button.config(state="normal", bg="lightgray", text="Start Client")
    stop_button.config(state="disabled", bg="red")
    update_status("Client stopped", "red")

# Main Client Logic
def run_client():
    """Main client logic."""
    global client_running
    t = time.time()

    filename = "Z:\\Project-Running\\Codes From DAQ\\time_bob0.csv"
    df = pd.read_csv(filename, header=None, names=["h", "v", "d", "a"])

    bob_h = df['h'].to_numpy()
    bob_v = df['v'].to_numpy()
    bob_d = df['d'].to_numpy()
    bob_a = df['a'].to_numpy()

    b_h = bob_h[bob_h != 0]
    b_v = bob_v[bob_v != 0]
    b_d = bob_d[bob_d != 0]
    b_a = bob_a[bob_a != 0]

    bob_data = []
    for i in range(len(b_h)):
        bob_data.append([b_h[i], 0, 0])
    for i in range(len(b_v)):
        bob_data.append([b_v[i], 0, 1])
    for i in range(len(b_d)):
        bob_data.append([b_d[i], 1, 0])
    for i in range(len(b_a)):
        bob_data.append([b_a[i], 1, 1])

    bob_data.sort()
    bdf = pd.DataFrame(bob_data, columns=["t", "ba", "bt"])
    b_bit = bdf["bt"].to_numpy()
    bdf2 = bdf[["t", "ba"]]
    bdf2.to_csv("Z:\\Project-Running\\Codes From DAQ\\bobdata.csv", header=False, index=False)

    HOST = "127.0.0.1"  # Use computer IP in case of two different machines
    PORT = 65432  # Port number should be the same for client and server program

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        update_status("Connecting to Alice...", "blue")
        s.connect((HOST, PORT))
        t_0 = int(s.recv(1024).decode())  # Receive t_0 from Alice
        update_status(f"Received t_0: {t_0}", "blue")

        size = int(os.path.getsize("Z:\\Project-Running\\Codes From DAQ\\bobdata.csv"))
        s.send(str(size).encode())

        with open("Z:\\Project-Running\\Codes From DAQ\\bobdata.csv", "rb") as f:
            update_status("Sending data to Alice...", "blue")
            while client_running:
                bob_data2 = f.read(1024)
                if not bob_data2:
                    break
                s.send(bob_data2)

        size1 = int(s.recv(16).decode())
        total_len = 0
        with open("Z:\\Project-Running\\Codes From DAQ\\bsiftedn.csv", "wb") as h:
            while client_running and total_len < size1:
                nrecv = s.recv(1024)
                if not nrecv:
                    break
                h.write(nrecv)
                total_len += len(nrecv)

        df2 = pd.read_csv("Z:\\Project-Running\\Codes From DAQ\\bsiftedn.csv", header=None, names=["na", "nb"])
        corr_n = df2["na"].to_numpy()
        corr_b = df2["nb"].to_numpy()

        b_key = []
        for i in range(len(corr_n)):
            b_key.append(b_bit[corr_b[i]])

        df3 = pd.DataFrame(b_key)
        df3.to_csv("Z:\\Project-Running\\Codes From DAQ\\bkey.csv", header=False, index=False)

        key_size = os.path.getsize("Z:\\Project-Running\\Codes From DAQ\\bkey.csv")
        s.send(str(key_size).encode())

        with open("Z:\\Project-Running\\Codes From DAQ\\bkey.csv", "rb") as fi:
            while client_running:
                bob_data = fi.read(1024)
                if not bob_data:
                    break
                s.send(bob_data)

    if client_running:
        # Calculate QBER based on key comparison
        akdf = pd.read_csv("Z:\\Project-Running\\Codes From DAQ\\akey.csv", header=None, names=["a"])
        a_key = akdf["a"].to_numpy()

        b_key = np.array(b_key)

        # Calculate bit error count
        bit_errors = np.sum(a_key != b_key)
        qber = bit_errors / len(a_key)

        # Update the GUI with QBER, Key Length and other information
        update_qber(qber)
        update_key_length(len(b_key))  # Show the length of the generated key
        update_status(f"Length of key generated: {len(b_key)}", "green")
        update_status(f"Execution time: {time.time() - t:.2f} seconds", "green")

# Initialize the tkinter GUI
root = Tk()
root.title("Bob Client Status")
root.geometry("400x400")

status_label = Label(root, text="Waiting to start client...", font=("Arial", 12))
status_label.pack(pady=20)

qber_label = Label(root, text="QBER: Not Calculated", font=("Arial", 12))
qber_label.pack(pady=5)

key_length_label = Label(root, text="Key Length: Not Calculated", font=("Arial", 12))
key_length_label.pack(pady=5)

start_button = Button(root, text="Start Client", font=("Arial", 12), bg="lightgray", command=start_client)
start_button.pack(pady=10)

stop_button = Button(root, text="Stop Client", font=("Arial", 12), bg="red", state="disabled", command=stop_client)
stop_button.pack(pady=10)

client_running = False
root.mainloop()
