# These two files contain the old Bob and Alice code, which does not include a graphical user interface (GUI).

1). OLD-Alice-Code.py
2). OLD-Bob-Code.py

# These files contain the updated code, which now includes a graphical user interface (GUI).
Files:
1). Alice.py
2). Bob.py

# User Manual and Implementation Report for Alice Server with GUI

User Manual

Overview: This application is a GUI-based server implementation for Alice, designed to interface with Bob in a quantum key distribution system. The server processes Alice's data, compares it with Bob's data, calculates QBER (Quantum Bit Error Rate), and displays the results.

A. System Requirements:

1) Python 3.8 or later
2) Required libraries: numpy, pandas, socket, tkinter, threading, scipy
3) A Windows or Linux-based operating system
4) Installation Steps
5) Ensure Python is Installed:
6) Download and install Python from Python's official website.
7) Install Required Libraries:
8) Run the following command in your terminal or command prompt:
      *pip install numpy pandas scipy*

B. Place Required Files:

1) Ensure the following CSV files are located in the specified directory:
       *time_alice0.csv*
2) Any other required files (frombob.csv, etc.)
3) Update the file paths in the script if needed.
                         Run the Program:
                                  Execute the script by running:
                                   python alice_server_gui.py


C. Using the Application

1) Launch the GUI:
2) Run the script. A window titled "Alice Server Status" will open.

# User Manual and Implementation Report for Bob Client with GUI

A. System Requirements

1) Python Version: Python 3.8 or later.
2) Required Libraries:
    numpy
    pandas
    socket
    tkinter
    threading

3) Operating System: Windows or Linux-based operating system.

B. Installation Steps
1. Ensure Python is Installed
   Download and install Python from Python's official website.

2. Install Required Libraries
  Run the following command in your terminal or command prompt to install the necessary libraries:
                                 *pip install numpy pandas*

C. Place Required Files

1) Ensure the following CSV files are located in the specified directory:
                                   *time_bob0.csv*
2) Any other required files (e.g., akey.csv, etc.) must also be in place.
3) Update the file paths in the script if your directory structure is different.

D. Run the Program

1) Navigate to the directory containing the script.
2) Execute the script by running:
                          *python bob_client_gui.py*
