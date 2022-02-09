import matplotlib.pyplot as plt
import numpy as np
import random
import ottoeplitz

""" 
Toeplitz Hashing Example
======================

In this example, we generate a large Gaussian input data set. We plot the data before
and after hashing. The data after hashing should be uniform.

"""

inputdata = []

for i in range(2**19):
    temp = random.gauss(5, .05)
    inputdata.append(temp)
inputdata = np.array(inputdata)

def plot_data(data, n):
        """ Bins up data and plots. """
        N, data = ottoeplitz.Toeplitz._calculate_N(data)
        # Bin up voltages and assign each bin a number from 0-255
        binned_data, bins = np.histogram(data, bins=2**n-1)            
        # Digitize raw data
        data_digital = np.digitize(data, bins, right=True)             
        # Plot histogram of raw digitized data
        fig, ax = plt.subplots()  
        ax.hist(data_digital,bins=2**n-1, label='Digitized Raw Data')
        plt.xlabel('Random numbers')
        plt.ylabel('Frequency')
        plt.title("Plotting Data Before and After Hashing")
        plt.show()
        return binned_data, data_digital       
    

t = ottoeplitz.Toeplitz(inputdata, 8)
plot_data(inputdata, 8)
dist = t.hash(8)
plot_data(dist, 8)