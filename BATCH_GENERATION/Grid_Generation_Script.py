"""
This script generates a 2D grid with a stochastic distribution of properties
It is not meant to be run directly, but rather to be imported in a batch generation script
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import sys
import os
import shutil

#dir_script = os.path.dirname(__file__)

#----------- PARAMETERS -------------
# Domain parameters
xmin = -250
xmax = 250
zmin = -100
zmax = 0
Lx = xmax - xmin
Lz = zmax - zmin
Nx = 500
Nz = 100


coeff = np.sqrt(2*(1-nu)/(1-2*nu))

# # Distribution parameters
# Lc_x = 2*Lx
# Lc_z = Lz/10
# nu_distrib = 1

# # Structure properties
# nu = 0.3
# coeff = np.sqrt(2*(1-nu)/(1-2*nu))
# Vs_struct = 300
# Vp_struct = Vs_struct*coeff
# rho_struct = 2000

# Script parameters
plotting = False


#-------- GRID READING ---------------
def read_grid(filepath):
    values = pd.read_csv(filepath, header=None).to_numpy()
    grid = np.array([])
    for i, line in enumerate(values):
        val = np.array(line[0].split(),dtype=float)
        if i%2==0:
            line_values = np.array([])
            line_values = np.concatenate([line_values, val], axis=0)
        else:
            line_values = np.concatenate([line_values, val], axis=0)
            if i==1:
                grid = np.concatenate([grid,line_values], axis=0)
            else:
                grid = np.vstack([grid,line_values])
    return grid

grid = read_grid(dir_script+'/USER_2D_grid.inp')
e, ii, jj, X_SEM, Z_SEM = grid[:,0].astype(int), grid[:,1].astype(int), grid[:,2].astype(int), grid[:,3], grid[:,4]

#---------- STOCHASTIC DISTRIBUTION FUNCTIONS ------------
def compute_spatial_frequencies(Lx, Lz, Nx, Nz):
    """ 
    Function which compute the spatial frequencies of a grid

    Parameters :
    Lx, Lz : Domain lengths
    Nx, Nz : Number of points in the domain
    """
    kx = 2*np.pi*np.fft.fftfreq(Nx, Lx/Nx)
    kz = 2*np.pi*np.fft.fftfreq(Nz, Lz/Nz)
    return kx, kz

def compute_Von_Karman_SPD(kx, kz, Lc_x, Lc_z, nu=1):
    """
    Function which compute the Spectral Power Density of a Von Karman distribution

    Parameters :
    kx, kz : Spatial frequencies (1D array)
    Lc_x, Lc_z : Typical length of variation (float)
    nu : Roughness parameter
    """
    Kx, Kz = np.meshgrid(kx,kz)
    kc_x = 1/Lc_x
    kc_z = 1/Lc_z
    S = 1 / (1 + (Kx/kc_x)**2 + (Kz/kc_z)**2)**(nu+1)
    return S

def compute_field(SPD):
    """
    Function which compute the field associated to a particular Spectral Power Density

    Parameters :
    SPD : Spectral Power Density (2D array)
    """
    W = np.random.normal(loc=0.0, scale=1.0, size=SPD.shape) #Compute a Gaussian White Field
    root = np.sqrt(SPD)
    G = np.fft.ifft2( root * np.fft.fft2(W) )
    return np.abs(G)

#--------- COMPUTATIONS -------------
#Stochastic Distribution
X = np.linspace(xmin, xmax, Nx)
Z = np.linspace(zmin, zmax, Nz)
kx, kz = compute_spatial_frequencies(Lx, Lz, Nx, Nz)
S = compute_Von_Karman_SPD(kx, kz, Lc_x, Lc_z, nu=nu_distrib)
G = compute_field(S)

if plotting:
    fig, ax = plt.subplots()
    im = ax.imshow(G, extent=[xmin, xmax, zmin, zmax])
    plt.colorbar(im, ax=ax)
    ax.set_title("Stochastic Grid Representation")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")
    ax.set_aspect('auto')
    plt.show()

# S-Wave Velocities
Vs_min = 100
Vs_max = 500
Vs = np.interp(G, (np.min(G), np.max(G)), (Vs_min, Vs_max))

# P-Wave Velocities
Vp_min = Vs_min*coeff
Vp_max = Vs_max*coeff
Vp = np.interp(G, (np.min(G), np.max(G)), (Vp_min, Vp_max))

# Densities
rho_min = 1500
rho_max = 3000
#rho = np.interp(G, (np.min(G), np.max(G)), (rho_min, rho_max))
rho = 2000*np.ones(Vs.shape)

# Masks
soil_mask = (Z_SEM <= 0)
structure_mask = (np.abs(Z_SEM) < 30) & (np.abs(X_SEM) < 10)

# Variables definition
X_stoch, Z_stoch = np.meshgrid(X,Z)
Vs_SEM = np.zeros(X_SEM.size)
Vp_SEM = np.zeros(X_SEM.size)
rho_SEM = np.zeros(X_SEM.size)

# Interpolation and mask applications
Vs_SEM[soil_mask] = griddata((X_stoch.flatten(), Z_stoch.flatten()), Vs.flatten(), (X_SEM[soil_mask],Z_SEM[soil_mask]), method='linear', fill_value=0)
Vs_SEM[structure_mask] = Vs_struct

Vp_SEM[soil_mask] = griddata((X_stoch.flatten(), Z_stoch.flatten()), Vp.flatten(), (X_SEM[soil_mask],Z_SEM[soil_mask]), method='linear', fill_value=0)
Vp_SEM[structure_mask] = Vp_struct

rho_SEM[soil_mask] = griddata((X_stoch.flatten(), Z_stoch.flatten()), rho.flatten(), (X_SEM[soil_mask],Z_SEM[soil_mask]), method='linear', fill_value=0)
rho_SEM[structure_mask] = rho_struct

#----------- EXPORT --------------
file = open(dir_output+'/USER_2D_grid_values.inp', 'w+')
for i in range(X_SEM.size):
    if i==X_SEM.size-1:
        file.write(f"{e[i]:12d}{ii[i]:12d}{jj[i]:12d}{Vs_SEM[i]:12.5f}{Vp_SEM[i]:12.5f}\n")
    else:
        file.write(f"{e[i]:12d}{ii[i]:12d}{jj[i]:12d}{Vs_SEM[i]:12.5f}{Vp_SEM[i]:12.5f}\n")
file.close()
shutil.copy2(dir_script+'/USER_2D_grid.inp', dir_output+'/USER_2D_grid.inp')