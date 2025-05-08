# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 17:23:28 2022

@author: ALICE
"""

import sys
import numpy as np
import socket
import csv
import pandas as pd
import os
import scipy.io as sio
import time
from tkinter import Tk, Label, Button
from threading import Thread

# Funtions used
# Label which shows message  i.e. Waiting for start server

def update_status(message, color="black"):
    """Update the status message on the GUI."""
    status_label.config(text=message, fg=color)
    root.update()

# Update qber, key length and execution time once code is updated
def update_additional_info(qber, key_length, execution_time):
    """Display additional information on the GUI."""
    qber_label.config(text=f"QBER: {qber * 100:.2f}%", fg="green")
    key_length_label.config(text=f"Key Length: {key_length}", fg="green")
    execution_time_label.config(text=f"Execution Time: {execution_time:.2f} seconds", fg="green")
    root.update()

# This function Starts Server
def start_server():
    """Start the server in a separate thread."""
    global server_running
    server_running = True
    start_button.config(state="disabled", bg="green", text="Server Running")
    stop_button.config(state="normal")
    Thread(target=run_server, daemon=True).start()

# This function Stops server
def stop_server():
    """Stop the server and update the GUI."""
    global server_running
    server_running = False
    start_button.config(state="normal", bg="lightgray", text="Start Server")
    stop_button.config(state="disabled", bg="red")
    update_status("Server stopped", "red")

# Function to implement logic
def run_server():
    """Main server logic."""
    global server_running
    t = time.time()
    filename = "Z:\\Project-Running\\Codes From DAQ\\time_alice0.csv"
    df = pd.read_csv(filename, header=None, names=["h", "v", "d", "a"])

    alice_h = df['h'].to_numpy()
    alice_v = df['v'].to_numpy()
    alice_d = df['d'].to_numpy()
    alice_a = df['a'].to_numpy()

    a_h = alice_h[alice_h != 0]
    a_v = alice_v[alice_v != 0]
    a_d = alice_d[alice_d != 0]
    a_a = alice_a[alice_a != 0]

    alice_data = []
    for i in range(len(a_h)):
        alice_data.append([a_h[i], 0, 0])

    for i in range(len(a_v)):
        alice_data.append([a_v[i], 0, 1])

    for i in range(len(a_d)):
        alice_data.append([a_d[i], 1, 0])

    for i in range(len(a_a)):
        alice_data.append([a_a[i], 1, 1])

    alice_data.sort()
    adf = pd.DataFrame(alice_data, columns=["t", "ba", "bt"])
    a_bas = adf["ba"].to_numpy()
    a_bit = adf["bt"].to_numpy()
    adf2 = adf[["t", "ba"]]
    a_t = adf["t"].to_numpy()
    t_0 = alice_data[0][0]
    adf2.to_csv("Z:\\Project-Running\\Codes From DAQ\\alicedata.csv", header=False, index=False)

    bob_n = []
    alice_n = []

    delay = 120

    HOST = "127.0.0.1"  # Use computer IP in case of two different machines
    PORT = 65432  # Port number should be the same for client and server program

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        update_status("Socket successfully created", "blue")
        s.bind((HOST, PORT))
        s.listen()
        update_status("Waiting for Bob to connect...", "blue")

        conn, addr = s.accept()
        update_status("Bob connected", "green")

        try:
            conn.send(str(t_0).encode())
            
            size = int(conn.recv(16).decode())
            update_status(f"Receiving data of size {size} from Bob...", "blue")

            total_len = 0
            with open("Z:\\Project-Running\\Codes From DAQ\\frombob.csv", "wb") as f:
                while server_running and total_len < size:
                    recv_data = conn.recv(1024)
                    if not recv_data:
                        break
                    f.write(recv_data)
                    total_len += len(recv_data)

            if not server_running:
                return

            df2 = pd.read_csv("Z:\\Project-Running\\Codes From DAQ\\frombob.csv", names=["t", "bas"])
            bob_t = df2['t'].to_numpy()
            b_bas = df2["bas"].to_numpy()

            for i in range(len(bob_t)):
                bob_n.append(int(round((bob_t[i] - t_0 - delay) / 200, 0)))

            for i in range(len(a_t)):
                alice_n.append(int(round((a_t[i] - t_0) / 200, 0)))

            correction_dict = {0: 0}
            correction_arr = [0]
            correction_factor = 0

            for i in range(1, len(a_t)):
                if a_t[i] - a_t[i - 1] > 250:
                    correction_factor += int(round((a_t[i] - a_t[i - 1]) / 200, 0)) - 1
                    correction_arr.append(correction_factor)
                    correction_dict[alice_n[i]] = correction_arr[i]
                else:
                    correction_arr.append(correction_factor)
                    correction_dict[alice_n[i]] = correction_arr[i]

            count = 0
            corr_n = []
            miscount = 0

            for i in range(len(b_bas)):
                if not server_running:
                    return
                try:
                    if b_bas[i] == a_bas[bob_n[i] - correction_dict[bob_n[i]]]:
                        count += 1
                        corr_n.append([bob_n[i] - correction_dict[bob_n[i]], i])
                except:
                    miscount += 1

            df3 = pd.DataFrame(corr_n)
            df3.to_csv("Z:\\Project-Running\\Codes From DAQ\\asiftedn.csv", header=False, index=False)

            size1 = os.path.getsize("Z:\\Project-Running\\Codes From DAQ\\asiftedn.csv")
            conn.send(str(size1).encode())
            with open("Z:\\Project-Running\\Codes From DAQ\\asiftedn.csv", "rb") as h:
                while server_running:
                    ndata = h.read(1024)
                    if not ndata:
                        break
                    conn.send(ndata)

            if not server_running:
                return

            a_key = []
            err = 0
            for i in range(len(corr_n)):
                if not server_running:
                    return
                try:
                    a_key.append(a_bit[corr_n[i][0]])
                except:
                    err += 1

            df4 = pd.DataFrame(a_key)
            df4.to_csv("Z:\\Project-Running\\Codes From DAQ\\akey.csv", header=False, index=False)

            key_len = int(conn.recv(16).decode())
            total_keylen = 0
            with open("Z:\\Project-Running\\Codes From DAQ\\bkey2.csv", "wb") as fi:
                while server_running and total_keylen < key_len:
                    recv_data = conn.recv(1024)
                    if not recv_data:
                        break
                    fi.write(recv_data)
                    total_keylen += len(recv_data)

        except ConnectionResetError:
            update_status("Client is closed", "red")
            return

    akdf = pd.read_csv("Z:\\Project-Running\\Codes From DAQ\\akey.csv", header=None, names=["a"])
    a_key = akdf["a"].to_numpy()
    bkdf = pd.read_csv("Z:\\Project-Running\\Codes From DAQ\\bkey2.csv", header=None, names=["b"])
    b_key = bkdf["b"].to_numpy()

    err_count = 0
    for i in range(len(a_key)):
        if not server_running:
            return
        if a_key[i] != b_key[i]:
            err_count += 1

    qber = (err_count) / len(a_key)
    execution_time = time.time() - t  # Existing execution time calculation

    # Update the additional information on the GUI
    update_additional_info(qber, len(a_key), execution_time)
    update_status(f"Server finished processing.", "green")

# Initialize the tkinter GUI
root = Tk()
root.title("Alice Server Status")
root.geometry("400x400")

status_label = Label(root, text="Waiting to start server...", font=("Arial", 12))
status_label.pack(pady=20)

qber_label = Label(root, text="QBER: Not Calculated", font=("Arial", 12))
qber_label.pack(pady=5)

key_length_label = Label(root, text="Key Length: Not Calculated", font=("Arial", 12))
key_length_label.pack(pady=5)

execution_time_label = Label(root, text="Execution Time: Not Calculated", font=("Arial", 12))
execution_time_label.pack(pady=5)

start_button = Button(root, text="Start Server", font=("Arial", 12), bg="lightgray", command=start_server)
start_button.pack(pady=10)

stop_button = Button(root, text="Stop Server", font=("Arial", 12), bg="red", state="disabled", command=stop_server)
stop_button.pack(pady=10)

server_running = False

root.mainloop()
