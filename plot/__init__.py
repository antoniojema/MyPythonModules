import matplotlib.pyplot as plt
import numpy as np

# A function that takes a file that contains 2 columns and plots them
def plot_2_columns(file_name, **kwargs):
    # Read the file
    data = np.loadtxt(file_name)
    # Plot the data
    plt.plot(data[:,0], data[:,1], **kwargs)
    # Show the plot
    plt.show()