import os
import numpy as np

def write_source_file(time, source):
    file = open(direct+'/source', 'w+')
    for i in range(source.size):
        file.write(f"{time[i]:2.6f}\t{source[i]:2.6f}\n")
    file.close()

def Gaussian_Source(t, f0, onset, ampli=1.):
    """
    Gaussian source function.
    """
    return ampli * np.exp(-((t - onset) ** 2) * (np.pi * f0) ** 2)

time = np.arange(0, t_max, 10*dt)
stf = Gaussian_Source(time, f0=f0, onset=onset, ampli=ampli)
write_source_file(time, stf)