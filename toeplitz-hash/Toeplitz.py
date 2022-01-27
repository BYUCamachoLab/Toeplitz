"""
toeplitz-hash.toeplitz
===============

This module contains the main ``Toeplitz`` class. This is where
the toeplitz hashing takes place.

"""

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

    # Import raw quantum data
    # time_stamp = "2021_8_11_15_57"
    time_stamp = "2021_7_6_10_52"
    z_measur = f"C:/Users/sarah/Box/CamachoLab/Christian/QRNG/data/{time_stamp}_data.p"
    z_data = pickle.load(open(z_measur, "rb"))
    data = np.array(z_data["z_powmeas"])[-1]


    # calculate_N may not need data as input because data is initialized in __init__
    def calculate_N(self, data):  # What does self mean? <----- Is there another file that is calling these funcions? How does it work?
        """ 
        Calculates a power of 2 closest to, but under, the size
        of the original input data. We call this power, N. Resizes 
        data by taking first 2^N data points and deleting the rest.

        Returns N and newly sized data.
        """
        N = 0 # Used to generate 2^N raw data points from normal distribution
        while (data.size - 2**N) >= 0:
            N += 1
        N -= 1
        indices = []
        for i in range(2**N, data.size):
            indices.append(i)
        data = np.delete(data, indices)
        return N, data
        
    # plot_data may not need data as input because data and n is initialized in __init__
    def plot_data(self, data, n):
        """ Bins up data and plots. """
        # Bin up voltages and assign each bin a number from 0-255
        binned_data, bins = np.histogram(data, bins=2**n-1)       # Do we need to separate binned_data from plot_data functions? <-----
        # Digitize raw data
        data_digital = np.digitize(data, bins, right=True) 
        # Plot histogram of raw digitized data
        fig, ax = plt.subplots()  # Where does fig come from? <--------
        ax.hist(data_digital,bins=2**n-1, label='Digitized Raw Data')
        ax.legend()
        plt.xlabel('Random numbers')
        plt.ylabel('Frequency')
        plt.title("-35 dbm measurements")
        plt.show()
        return binned_data #fixme: idk if this is what we want to return <----- 

    def min_entropy(self, N, binned_data):
        """Calculates the minimum entropy of the data.

        Parameters
        ----------
        N :
            a power of 2 closest to, but under, the size
            of the original input data.
        binned_data :
            The input data of size 2^N binned up into 
            2^n bins.

        Returns minimum entropy.
        """
        # Find probability max
        pmax = np.max(binned_data)/2**N
        # Find minimum-entropy
        min_ent = -np.log2(pmax)
        return min_ent

    # Find output length
    def output_length(self):
        """ 
        Calculates length of the output data using min-entropy.

        Returns output length.
        """
        N, data
        min_ent = min_entropy(data, )
        out_len = 2**n * (min_ent/n)
        out_len = round(out_len)
        return out_len

    # Generate random 2^n by 2^m toeplitz matrix
    def toep_mat(self, out_len, n):
        """
        Constructs a random n x m binary Toeplitz matrix.
        
        Returns constructed Toeplitz matrix.
        """
        row = np.random.randint(2, size=out_len)
        col = np.random.randint(2, size=2**n)
        toep_mat = toeplitz(row, col)
        return toep_mat

    # Convert digitized raw data to binary
    def decToBin_data(self, data_digital, N):
        """
        Converts data from decimal to binary.

        Returns flattened array of the binary data.
        """
        def decToBin(data_pt, depth, bin_pts): # Where does bin_pts come from? <-----
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
    def toeplitz_hash(self, data_flat, m, n, N, toep_mat):
        """
        Performs the Toeplitz hashing.

        Returns digitized hashed data.
        """
        # Split digitized data into chunks of size 2^n
        split = np.array_split(data_flat, n * 2**(N-n)) 
        # perform matrix multiplication of Toeplitz with data chunks
        data_hashed = np.dot(toep_mat, split[0]) % 2
        for index, data in enumerate(split[1:-1]):  # What is index? <----- Should this data be data_flat? <-----
            sample_hashed = np.dot(toep_mat, data) % 2  # Should this data be data_flat? <-----
            data_hashed = np.append(data_hashed, sample_hashed)
        # split hashed data into chunks of size 2^n
        data_hashed = np.array_split(data_hashed, m * 2**(N-n))
        decimal = []
        for index, sample in enumerate(data_hashed): # Index? Do we need it? <-----
            x = ''.join([str(int(elem)) for elem in sample])
            decimal = np.append(decimal, int(x, 2))
        decimal = decimal[decimal != 255]
        return decimal #?? <-----
   

