# the program is used to plot a binary matrix, and visualize the plot 
# which updates in 1 second
#use ipython interface, jupyter notebook do not shows the animated plot for this# code, normal python excution is okay though show some warning (DS)n

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Function to generate a random 100x100 binary matrix
def generate_matrix():
    return np.random.choice([0, 1], size=(1080, 1920))

# Initialize the matrix
matrix = generate_matrix()

# Set up the figure and axis for plotting
fig, ax = plt.subplots()
cax = ax.matshow(matrix, cmap='gray')

# Function to update the plot
def update(frame):
    global matrix
    # Update the matrix (you can define your own logic here)
    matrix = generate_matrix()
    cax.set_array(matrix)
    return cax,

# Create an animation that updates every 1000 milliseconds (1 second)
ani = FuncAnimation(fig, update, interval=1000)

# Show the plot in a GUI window
plt.show()

