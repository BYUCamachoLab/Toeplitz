"""
toeplitz-hash.toeplitz
===============

This module contains the main ``Toeplitz`` class. This is where
the toeplitz hashing takes place.

"""

from typing import Callable
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.constants import *
from scipy.linalg import toeplitz

class Toeplitz:
    """ 
    The ``Toeplitz`` class executes the toeplitz hashing. It 
    requires a large set of random data and the resolution of your
    ADC as input.

    """

    def __init__(self, data, n):
        self.bits = 8
        self.data = data
        self.n = n

    def calculate_N(self):  
        """ 
        Calculates a power of 2 closest to, but under, the size
        of the original input data. We call this power, N. Resizes 
        data by taking first 2^N data points and deleting the rest.

        Returns N and newly sized data.
        """
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
        """ Bins up data and plots. """
        #calculate_N(self, data)
        #N = calculate_N.N
        N, data = self.calculate_N(self, self.data)
        # Bin up voltages and assign each bin a number from 0-255
        binned_data, bins = np.histogram(data, bins=2**n-1)            
        # Digitize raw data
        data_digital = np.digitize(data, bins, right=True)             
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
        """Calculates the minimum entropy of the data.

        Returns minimum entropy.
        """
        binned_data, data_digital = self.plot_data(self.n)                              
        N, data = self.calculate_N(self, self.data)
        # Find probability max
        pmax = np.max(binned_data)/2**N                                 
        # Find minimum-entropy
        min_ent = -np.log2(pmax)                                       
        return min_ent                                                

    # Find output length
    def output_length(self, n):  
        """ 
        Calculates length of the output data using min-entropy.

        Returns output length.
        """                             
        binned_data, data_digital = self.plot_data(n)  
        min_ent = self.min_entropy(binned_data)
        out_len = 2**n * (min_ent/n)                                    
        out_len = round(out_len)
        return out_len                                                 

    # Generate random 2^n by 2^m toeplitz matrix
    def toep_mat(self, n):
        """
        Constructs a random n x m binary Toeplitz matrix.
        
        Returns constructed Toeplitz matrix.
        """
        out_len = self.output_length(n)
        row = np.random.randint(2, size=out_len)                        
        col = np.random.randint(2, size=2**n)
        toep_mat = toeplitz(row, col)                                    
        return toep_mat                                                 

    # Convert digitized raw data to binary
    def decToBin_data(self):   
        """
        Converts data from decimal to binary.

        Returns flattened array of the binary data.
        """                   
        N, data = self.calculate_N(self.data)
        binned_data, data_digital = self.plot_data(self.n)  
        def decToBin(data_pt, depth, bin_pts): 
            """ 
            General function converting decimal to binary.

            Parameters
            ----------
            data_pt :
                Number you want to convert to binary.
            depth :
                How many bits you want the number represented with.
            bin_pts :
                Recursive part of function.
            
            Returns binary number.
            """
            if data_pt >= 1:
                bin_pts = decToBin(data_pt // 2, depth - 1, bin_pts)
                bin_pts[depth] = data_pt % 2
            return bin_pts
        binary_data = []
        for i in range(2**N):
            zeros = np.zeros(8)
            binary_data.append(decToBin(data_digital[i], 7, zeros))      
        binary_data = np.reshape(binary_data, (2**N, 8))
        data_flat = binary_data.flatten()                                
        return data_flat

    # Toeplitz Hash function
    def toeplitz_hash(self, n):
        """
        Performs the Toeplitz hashing.

        Returns digitized hashed data.
        """
        N, data = self.calculate_N(self.data)
        out_len = self.output_length(self.n)
        data_flat = self.decToBin_data()
        toep_mat = self.toep_mat(self.n)
        # Split digitized data into chunks of size 2^n                     
        split = np.array_split(data_flat, n * 2**(N-n))                 
        # perform matrix multiplication of Toeplitz with data chunks
        data_hashed = np.dot(toep_mat, split[0]) % 2
        for index, data in enumerate(split[1:-1]):  
            sample_hashed = np.dot(toep_mat, data) % 2 
            data_hashed = np.append(data_hashed, sample_hashed)
        # split hashed data into chunks of size 2^n
        data_hashed = np.array_split(data_hashed, out_len * 2**(N-n))            
        decimal = []                                                       
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
