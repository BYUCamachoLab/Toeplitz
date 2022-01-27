# Toeplitz

toeplitz-hash
--------

Toeplitz hashing algorithm for post-processing quantum random number generation

Should I relate the description to general random distributions or quantum experiment and others like it?

In QRNG, a quantum state is prepared and a measurement is preformed on the state. However, because of imperfections in the experiment, the quantum signal is inevitably mixed with classical noise. QRNG, thus, requires some post-processing in order to extract the true randomness and eliminate the contributions of said noise. In our experiment, we use a Toeplitz hash extraction algorithm to process the raw data. Because our raw data is Gaussian in nature (thus, some numbers are more likely than others), the goal of this hash extraction is to suppress the classical contributions to construct a more uniform distribution of our random data.

The procedure of Toeplitz hashing starts with some raw data of size n (produced by the measurement of the quantum state) with a min-entropy of k (the lower bound on its randomness) and a security parameter ε. For example, if we start with an input bit-length of 8 and our min-entropy is 6.7, we can extract 6.7 random bits per 8 bits of raw data, or 80%. With this information, we can find the output length, m. We then construct a Toeplitz matrix with an n + m - 1 random-bit seed and multiply this matrix with the raw data to produce the extracted random data. 