from typing import Callable
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.constants import *
from scipy.linalg import toeplitz

class Toeplitz:
    def __init__(self, data, n):
        self.bits = 8
        self.data = data
        self.n = n

    def calculate_N(self):  
        N = 0 # Used to generate 2^N raw data points from normal distribution
        while (self.data.size - 2**N) >= 0:
            N += 1
        N -= 1
        indices = []
        for i in range(2**N, self.data.size):
            indices.append(i)
        data = np.delete(self.data, indices)
        return N, data
    
    #N, data = calculate_N(self, data)

    def plot_data(self, n):
        #calculate_N(self, data)
        #N = calculate_N.N
        N, data = self.calculate_N(self, self.data)
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

    def min_entropy(self):  
        binned_data, data_digital = self.plot_data(self.n)                              
        N, data = self.calculate_N(self, self.data)
        # Find probability max
        pmax = np.max(binned_data)/2**N                                  #call for binned_data
        # Find minimum-entropy
        min_ent = -np.log2(pmax)                                         #min_ent created
        return min_ent                                                

    # Find output length
    def output_length(self, n):                                 #call for min_ent
        binned_data, data_digital = self.plot_data(n)  
        min_ent = self.min_entropy(binned_data)
        out_len = 2**n * (min_ent/n)                                     #out_len created
        out_len = round(out_len)
        return out_len                                                 

    # Generate random 2^n by 2^m toeplitz matrix
    def toep_mat(self, n):
        out_len = self.output_length(n)
        row = np.random.randint(2, size=out_len)                         #call for out_len
        col = np.random.randint(2, size=2**n)
        toep_mat = toeplitz(row, col)                                    #toep_mat created
        return toep_mat                                                 

    # Convert digitized raw data to binary
    def decToBin_data(self):                            #call for data_digital
        N, data = self.calculate_N(self.data)
        binned_data, data_digital = self.plot_data(self.n)  
        def decToBin(data_pt, depth, bin_pts): 
            if data_pt >= 1:
                bin_pts = decToBin(data_pt // 2, depth - 1, bin_pts)
                bin_pts[depth] = data_pt % 2
            return bin_pts
        binary_data = []
        for i in range(2**N):
            zeros = np.zeros(8)
            binary_data.append(decToBin(data_digital[i], 7, zeros))      #call for data_digital ---------- ???
        binary_data = np.reshape(binary_data, (2**N, 8))
        data_flat = binary_data.flatten()                                #data_flat created
        return data_flat

    # Toeplitz Hash function
    def toeplitz_hash(self, n):
        N, data = self.calculate_N(self.data)
        out_len = self.output_length(self.n)
        data_flat = self.decToBin_data()
        toep_mat = self.toep_mat(self.n)
        # Split digitized data into chunks of size 2^n                      #call for N
        split = np.array_split(data_flat, n * 2**(N-n))                  #call for data_flat
        # perform matrix multiplication of Toeplitz with data chunks
        data_hashed = np.dot(toep_mat, split[0]) % 2
        for index, data in enumerate(split[1:-1]):  
            sample_hashed = np.dot(toep_mat, data) % 2 
            data_hashed = np.append(data_hashed, sample_hashed)
        # split hashed data into chunks of size 2^n
        data_hashed = np.array_split(data_hashed, out_len * 2**(N-n))             #call for out_len
        decimal = []                                                        #decimal created
        for index, sample in enumerate(data_hashed): 
            x = ''.join([str(int(elem)) for elem in sample])
            decimal = np.append(decimal, int(x, 2))
        decimal = decimal[decimal != 255]
        return decimal 
   

if __name__ == "__main__":
    # Import raw quantum data
    # time_stamp = "2021_8_11_15_57"
    time_stamp = "2021_7_6_10_52"
    z_measur = f"C:/Users/sarah/Box/CamachoLab/Christian/QRNG/data/{time_stamp}_data.p"
    z_data = pickle.load(open(z_measur, "rb"))
    data = np.array(z_data["z_powmeas"])[-1]

    t = Toeplitz(data, 8)
