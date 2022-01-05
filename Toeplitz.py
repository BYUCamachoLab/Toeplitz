from typing import Callable
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.constants import *
from scipy.linalg import toeplitz

class Toeplitz:
    def __init__(self):
        self.bits = 8

    # Import raw quantum data
    # time_stamp = "2021_8_11_15_57"
    time_stamp = "2021_7_6_10_52"
    z_measur = f"C:/Users/sarah/Box/CamachoLab/Christian/QRNG/data/{time_stamp}_data.p"
    z_data = pickle.load(open(z_measur, "rb"))
    data = np.array(z_data["z_powmeas"])[-1]


    def calculate_N(self, data):  
        N = 0 # Used to generate 2^N raw data points from normal distribution
        while (data.size - 2**N) >= 0:
            N += 1
        N -= 1
        indices = []
        for i in range(2**N, data.size):
            indices.append(i)
        data = np.delete(data, indices)
        return N, data
        

    def plot_data(self, data, n):
        # Bin up voltages and assign each bin a number from 0-255
        binned_data, bins = np.histogram(data, bins=2**n-1)             #binned_data created
        # Digitize raw data
        data_digital = np.digitize(data, bins, right=True)              #data_digital created
        # Plot histogram of raw digitized data
        fig, ax = plt.subplots()  
        ax.hist(data_digital,bins=2**n-1, label='Digitized Raw Data')
        ax.legend()
        plt.xlabel('Random numbers')
        plt.ylabel('Frequency')
        plt.title("-35 dbm measurements")
        plt.show()
        return binned_data, data_digital                               

    def min_entropy(self, binned_data):                                  
        N, data = calculate_N(self, binned_data)
        # Find probability max
        pmax = np.max(binned_data)/2**N                                  #call for binned_data
        # Find minimum-entropy
        min_ent = -np.log2(pmax)                                         #min_ent created
        return min_ent                                                

    # Find output length
    def output_length(self, n, min_ent):                                 #call for min_ent
        out_len = 2**n * (min_ent/n)                                     #out_len created
        out_len = round(out_len)
        return out_len                                                 

    # Generate random 2^n by 2^m toeplitz matrix
    def toep_mat(self, out_len, n):
        row = np.random.randint(2, size=out_len)                         #call for out_len
        col = np.random.randint(2, size=2**n)
        toep_mat = toeplitz(row, col)                                    #toep_mat created
        return toep_mat                                                 

    # Convert digitized raw data to binary
    def decToBin_data(self, data_digital, N):                            #call for data_digital
        def decToBin(data_pt, depth, bin_pts): 
            if data_pt >= 1:
                bin_pts = decToBin(data_pt // 2, depth - 1, bin_pts)
                bin_pts[depth] = data_pt % 2
            return bin_pts
        binary_data = []
        for i in range(2**N):
            zeros = np.zeros(8)
            binary_data.append(decToBin(data_digital[i], 7, zeros))      #call for data_digital
        binary_data = np.reshape(binary_data, (2**N, 8))
        data_flat = binary_data.flatten()                                #data_flat created
        return data_flat

    # Toeplitz Hash function
    def toeplitz_hash(self, data_flat, m, n, N, toep_mat):
        # Split digitized data into chunks of size 2^n                      #call for N
        split = np.array_split(data_flat, n * 2**(N-n))                  #call for data_flat
        # perform matrix multiplication of Toeplitz with data chunks
        data_hashed = np.dot(toep_mat, split[0]) % 2
        for index, data in enumerate(split[1:-1]):  
            sample_hashed = np.dot(toep_mat, data) % 2 
            data_hashed = np.append(data_hashed, sample_hashed)
        # split hashed data into chunks of size 2^n
        data_hashed = np.array_split(data_hashed, m * 2**(N-n))             #call for m?
        decimal = []                                                        #decimal created
        for index, sample in enumerate(data_hashed): 
            x = ''.join([str(int(elem)) for elem in sample])
            decimal = np.append(decimal, int(x, 2))
        decimal = decimal[decimal != 255]
        return decimal 
   

