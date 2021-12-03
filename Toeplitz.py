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

        new_data = np.delete(data, indices)
        return new_data
        

    def plot_data(self, new_data, n): # added n parameter <-----
        # Bin up voltages and assign each bin a number from 0-255
        binned_data, bins = np.histogram(new_data, bins=2**n-1) 
        data_digital = np.digitize(new_data, bins, right=True) # Digitize raw data

        # Plot histogram of raw digitized data
        fig, ax = plt.subplots()
        ax.hist(data_digital,bins=2**n-1, label='Digitized Raw Data')
        ax.legend()
        plt.xlabel('Random numbers')
        plt.ylabel('Frequency')
        plt.title("-35 dbm measurements")
        plt.show()
        return binned_data #fixme: idk if this is what we want to return <----- 

    # Calculate signal to noise and quantum standard deviation block? <-----

    def min_entropy(self, binned_data, N): # added 2 parameters <-----
        # Find probability max
        pmax = np.max(binned_data)/2**N

        # Find minimum-entropy
        min_ent = -np.log2(pmax)
        #quant_ent = min_ent * (-(1/(sig2noise + 1)) + 1)

        # Calculate security parameter 
        #secur_param = 2**(-100) # do we need to include security parameter? probably not for now? <-----

        return min_ent

    # Find output length
    def output_length(self, n, min_ent): # added 2 params, deleted data param<-----
        #m = min_ent - 2 * np.log2(secur_param)
        m = 2**n * (min_ent/n)
        m = round(m)
        return m

    # Generate random 2^n by 2^m toeplitz matrix
    def toep_mat(self, out_len, n): # deleted data param <-----
        row = np.random.randint(2, size=out_len)
        col = np.random.randint(2, size=2**n)
        toep_mat = toeplitz(row, col)
        return toep_mat

    # Convert digitized raw data to binary
    def decToBin_data(self, data): #fixme: params <-----
        def decToBin(data_pt, depth, bin_pts): # Where does bin_pts come from? <-----
            if data_pt >= 1:
                bin_pts = decToBin(data_pt // 2, depth - 1, bin_pts)
                bin_pts[depth] = data_pt % 2
            return bin_pts
        binary_data = []
        for i in range(2**N):
            zeros = np.zeros(8)
            binary_data.append(decToBin(data_digital[i], 7, zeros)) #where does data_digital come from? <-----
        binary_data = np.reshape(binary_data, (2**N, 8))
        data_flat = binary_data.flatten()
        return data_flat # fixme: return statement <-----

    # Toeplitz Hash function
    def toeplitz_hash(self, data):
        # tempN = 15

        # Split data into smaller chunks of size 2^tempN so it doesn't time out
        # chunks = np.array_split(data_flat, n * 2**(N-tempN))
        # print(len(chunks))

        # for i, data in enumerate(chunks):
        # Split digitized data into chunks of size 2^n
        split = np.array_split(data_flat, n * 2**(N-n)) 

        # perform matrix multiplication of Toeplitz with data chunks
        data_hashed = np.dot(toep_mat, split[0]) % 2
        for index, data in enumerate(split[1:-1]):
            sample_hashed = np.dot(toep_mat, data) % 2
            data_hashed = np.append(data_hashed, sample_hashed)
            
        # f = open("binary.txt", "w")
        # for i in range(len(data_hashed)):
        #     f.write(str(int(data_hashed[i])))
        # f.close()

        # split hashed data into chunks of size 2^n
        data_hashed = np.array_split(data_hashed, m * 2**(N-n))
        print(data_hashed[0:10])

        decimal = []
        for index, sample in enumerate(data_hashed):
            x = ''.join([str(int(elem)) for elem in sample])
            decimal = np.append(decimal, int(x, 2))
        decimal = decimal[decimal != 255]
        pass #fixme: return statement

    

