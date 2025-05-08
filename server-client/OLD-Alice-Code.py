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

t = time.time()
filename = "Z:\Project-Running\Codes From DAQ\\time_alice0.csv"
df=pd.read_csv(filename, header=None, names=["h","v","d","a"])

alice_h = df['h'].to_numpy()
alice_v = df['v'].to_numpy()
alice_d = df['d'].to_numpy()
alice_a = df['a'].to_numpy()

a_h = alice_h[alice_h!=0]
a_v = alice_v[alice_v!=0]
a_d = alice_d[alice_d!=0]
a_a = alice_a[alice_a!=0]

alice_data = []
for i in range(len(a_h)):
    alice_data.append([a_h[i],0,0])

for i in range(len(a_v)):
    alice_data.append([a_v[i],0,1])

for i in range(len(a_d)):
    alice_data.append([a_d[i],1,0])

for i in range(len(a_a)):
    alice_data.append([a_a[i],1,1])
    

alice_data.sort()
adf = pd.DataFrame(alice_data, columns=["t","ba","bt"])
a_bas = adf["ba"].to_numpy()
a_bit = adf["bt"].to_numpy()
adf2 = adf[["t","ba"]]
a_t = adf["t"].to_numpy()
t_0 = alice_data[0][0]
adf2.to_csv("Z:\Project-Running\Codes From DAQ\\alicedata.csv", header = False, index = False)

bob_n = [];
alice_n = [];

delay = 120;


HOST = "127.0.0.1" # use computer ip in case of two different machines
PORT = 65432  #port number should be same for client and server program

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("Socket successfully created")
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    print("Bob connected")
    conn.send(str(t_0).encode())
 
    size = int(conn.recv(16).decode())
    print(size)
    total_len = 0
    with open("Z:\Project-Running\Codes From DAQ\\frombob.csv", "wb") as f:         #receive time stamps and bases from Bob
        while total_len<size:
            recv_data = conn.recv(1024)
            if not recv_data:
                break
            f.write(recv_data)
            total_len = total_len + len(recv_data)
           
    df2 = pd.read_csv("Z:\Project-Running\Codes From DAQ\\frombob.csv", names = ["t","bas"]);
    bob_t = df2['t'].to_numpy()
    b_bas = df2["bas"].to_numpy()
    
    for i in range(len(bob_t)):
        bob_n.append(int(round((bob_t[i]-t_0-delay)/200,0)))
    
    for i in range(len(a_t)):
        alice_n.append(int(round((a_t[i]-t_0)/200,0)))
    
    correction_dict = {0:0}
    correction_arr = [0]
    correction_factor = 0

    for i in range(1, len(a_t)):
        if a_t[i]-a_t[i-1]>250:
            correction_factor = correction_factor + int(round((a_t[i]-a_t[i-1])/200,0)) - 1
            correction_arr.append(correction_factor)
            correction_dict[alice_n[i]] = correction_arr[i]
        else:
            correction_factor = correction_factor + 0
            correction_arr.append(correction_factor)
            correction_dict[alice_n[i]] = correction_arr[i]
    count = 0;
    corr_n = [];
    not_count = 0;
    # for i in range(len(b_bas)):
    #     if bob_n[i]<=len(alice_data):
    #         try:
    #             if a_bas[bob_n[i]-correction_arr[bob_n[i]]] == b_bas[i]:
    #                 count = count+1
    #                 corr_n.append([bob_n[i],i])
    #         except ValueError:
    #             not_count = not_count+1
                
    miscount = 0

    for i in range(len(b_bas)):
        try:
            if b_bas[i] == a_bas[bob_n[i] - correction_dict[bob_n[i]]]:
                # akey.append(a_bit[bob_n[i] - correction_dict[bob_n[i]]])
                # bkey.append(b_bit[i])
                count = count+1
                corr_n.append([bob_n[i] - correction_dict[bob_n[i]],i])
        except:
            miscount = miscount+1
                
    df3 = pd.DataFrame(corr_n)
    df3.to_csv("Z:\Project-Running\Codes From DAQ\\asiftedn.csv", header = False, index = False)
    
    size1 = os.path.getsize("Z:\Project-Running\Codes From DAQ\\asiftedn.csv")
    #print(size)
    conn.send(str(size1).encode())
    with open("Z:\Project-Running\Codes From DAQ\\asiftedn.csv","rb") as h:          #send sifted timestamps to Bob
        while True:
            ndata = h.read(1024)
            if not ndata:
                break
            conn.send(ndata)
            
    a_key = [];
    err = 0;
    for i in range(len(corr_n)):
        try:
            a_key.append(a_bit[corr_n[i][0]])
        except:
            err = err+1
            
    df4 = pd.DataFrame(a_key)
    df4.to_csv("Z:\Project-Running\Codes From DAQ\\akey.csv", header = False, index = False)
    
    # confirm = conn.recv(1024).decode()
    # print(confirm)                        # Sifted key done
    key_len = int(conn.recv(16).decode())
    total_keylen = 0
    with open("Z:\Project-Running\Codes From DAQ\\bkey2.csv", "wb") as fi:         #receive key from Bob
        while total_keylen<key_len:
            recv_data = conn.recv(1024)
            if not recv_data:
                break
            fi.write(recv_data)
            total_keylen = total_keylen + len(recv_data)
            
akdf = pd.read_csv("Z:\Project-Running\Codes From DAQ\\akey.csv", header=None, names=["a"])
a_key = akdf["a"].to_numpy()
bkdf = pd.read_csv("Z:\Project-Running\Codes From DAQ\\bkey2.csv", header=None, names=["b"])
b_key = bkdf["b"].to_numpy()
err_count = 0
for i in range(len(a_key)):
    if a_key[i]!=b_key[i]:
        err_count=err_count+1

qber = (err_count)/len(a_key)
print("QBER is:", qber*100)
print("length of key generated is:", len(a_key))
print(time.time()-t)