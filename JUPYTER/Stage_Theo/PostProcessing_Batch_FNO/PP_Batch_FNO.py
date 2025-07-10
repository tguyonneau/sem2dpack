#import libraries
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
from scipy.optimize import curve_fit
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# Add the parent directory and modules directory to the system path
sys.path.append(os.path.dirname(__file__)+'/../../')
sys.path.append(os.path.dirname(__file__)+'/../../modules')

# Import custom modules
from Class_sem2dpack import *
from Stage_module import *
is_overburden = False
fmin, fmax = 0.01, 10.0
#----------------------------------------------------------------

L = [40, 200, 1000]
f = [0.5, 1, 2, 5]
I = [0, 15, 30, 45, 60]
N = 5
dataset_directory = "C:/Users/t.guyonneau/OneDrive - EGIS Group/Documents/OUTPUT/Dataset_2/"

#-------------------------------------------------------------

Nx = 64
Ny = 64
Nt = 70
xmin, xmax = -250, 250
zmin, zmax = -100, 30
depth = 100
ZOI_xmin, ZOI_xmax = -depth/2, depth/2
ZOI_zmin, ZOI_zmax = -depth, 0

gridmode = 'ZOI' # ZOI or Global

def process_fault_data(SEM):
    fault_data = {}
    
    # Read fault data for different tags
    read_fault_testing(SEM, ftag=5)
    fault_data['Bottom'] = SEM.fault

    read_fault_testing(SEM, ftag=7)
    fault_data['Right'] = SEM.fault

    read_fault_testing(SEM, ftag=9)
    fault_data['Left'] = SEM.fault

    # Extract the coordinates and slip values for each fault component
    fault_components = {}
    for key, data in fault_data.items():
        X_coord = data['x']
        Z_coord = data['z']
        Slip_1 = data['Slip_1']
        Slip_2 = data['Slip_2']
        orientation = 'Z' if key in ['Left', 'Right'] else 'X'
        Peak_Sliding = np.max( np.max(np.abs(Slip_1), axis=1) )
        Peak_Uplift = np.max( np.max(np.abs(Slip_2), axis=1) )
        fault_components[key] = {
            'X_fault': X_coord, 
            'Z_fault': Z_coord,
            'Slip_1': Slip_1,
            'Slip_2': Slip_2,
            'orientation': orientation,
            'Peak_Sliding': Peak_Sliding,
            'Peak_Uplift': Peak_Uplift
            }
        

    # Extract the time data (assuming it's the same for all components)
    time_fault = fault_data['Left']['Time']

    return fault_components, time_fault

def create_path(SEM,comp,t):
        n = f"{t:03d}"
        path = SEM.directory + f'v{comp}_{n}_sem2d.dat'
        return path

def load_field(SEM, comp, t):
    X_Coord, Z_Coord = SEM.mdict["coord"][:,0] , SEM.mdict["coord"][:,1]
    path = create_path(SEM,comp, t)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} does not exist.")
    field = SEM.readField(path)
    return X_Coord, Z_Coord, field

def process_station_data(SEM):
    # Read Input Signal
    input_signal_path = SEM.directory+'/source'
    input_signal = np.genfromtxt(open(input_signal_path,'r'))
    time_input = input_signal[:,0]
    V_input = input_signal[:,1]

    # Read the X component of stations data
    SEM.read_seismo('x')
    SEM.filter_seismo(fmin, fmax)
    Time_stations = SEM.time
    Vx = SEM.velocity[:,:]
    Ux = np.zeros(Vx.shape, dtype=np.float32)
    Ax = np.zeros(Vx.shape, dtype=np.float32)
    for i in range(Vx.shape[1]):
        V = Vx[:,i]
        Ux[:,i] = compute_displacement(V, Time_stations)
        Ax[:,i] = compute_acceleration(V, Time_stations)
        

    # Read the Z component of stations data
    SEM.read_seismo('z')
    SEM.filter_seismo(fmin, fmax)
    Vz = SEM.velocity[:,:]
    Uz = np.zeros(Vz.shape, dtype=np.float32)
    Az = np.zeros(Vz.shape, dtype=np.float32)
    for i in range(Vz.shape[1]):
        V = Vz[:,i]
        Uz[:,i] = compute_displacement(V, Time_stations)
        Az[:,i] = compute_acceleration(V, Time_stations)

    # Read stations coordinates
    XSTA, ZSTA = SEM.rcoord[:,0], SEM.rcoord[:,1]

    # Read Snapshots data
    for i in range(0,Time_stations.size):
        try : 
            if i==0:
                X_snap, Z_snap, Vx_snap = load_field(SEM, 'x', i)
                _, _, Vz_snap = load_field(SEM, 'z', i)
                Vx_snap = np.expand_dims(Vx_snap, axis=1)
                Vz_snap = np.expand_dims(Vz_snap, axis=1)
            else :
                _, _, Vx_temp = load_field(SEM, 'x', i)
                _, _, Vz_temp = load_field(SEM, 'z', i)
                Vx_snap = np.concatenate([Vx_snap, np.expand_dims(Vx_temp, axis=1)], axis=1)
                Vz_snap = np.concatenate([Vz_snap, np.expand_dims(Vz_temp, axis=1)], axis=1)
        except FileNotFoundError:
            break


    # Compute PGD, PGV and PGA
    PGDx = np.max(np.abs(Ux), axis=0)
    PGDz = np.max(np.abs(Uz), axis=0)
    PGVx = np.max(np.abs(Vx), axis=0)
    PGVz = np.max(np.abs(Vz), axis=0)
    PGAx = np.max(np.abs(Ax), axis=0)
    PGAz = np.max(np.abs(Az), axis=0)
    

    # Create a dictionary to hold the components of the stations data
    components = {}
    components['time_input'] = time_input
    components['V_input'] = V_input
    components['X_station'] = XSTA
    components['Z_station'] = ZSTA
    components['Ux'] = Ux
    components['Uz'] = Uz
    components['Vx'] = Vx
    components['Vz'] = Vz
    components['Ax'] = Ax
    components['Az'] = Az
    components['PGDx'] = PGDx
    components['PGDz'] = PGDz
    components['PGVx'] = PGVx
    components['PGVz'] = PGVz
    components['PGAx'] = PGAx
    components['PGAz'] = PGAz
    components['X_snap'] = X_snap
    components['Z_snap'] = Z_snap
    components['Vx_snap'] = Vx_snap
    components['Vz_snap'] = Vz_snap
    return components, Time_stations

def process_grid_data(SEM):
    SEM_grid = import_SEM_grid(SEM.directory)
    print("Grid data processed for SEM:", SEM.directory)
    X = SEM_grid['X_grid']
    Z = SEM_grid['Z_grid']
    Vs = SEM_grid['Vs']
    return SEM_grid

def make_ZOI_mask(X, Z):
    if gridmode=='ZOI':
        ZOI_mask = (ZOI_xmin < X) & (X< ZOI_xmax) & (ZOI_zmin < Z) & (Z < ZOI_zmax)
    elif gridmode=='Global':
        ZOI_mask = np.ones_like(X, dtype=bool)
    else:
        raise Exception("Undefined gridmode")
    return ZOI_mask

def export_data():
    e=0
    for length in L:
        for frequency in f:
            for angle in I:
                for n in range(N):
                    # Load data
                    direct = dataset_directory + f"Batch_L_{length:d}_f_{10*frequency:02.0f}_I_{angle:02.0f}/Run_{n:02d}"
                    try :
                        if e>110:
                            SEM = sem2dpack(direct)
                            sim_components = {'Lc_x': length, 'f0': frequency, 'angle': angle}
                            fault_components, time_fault = process_fault_data(SEM)
                            station_components, time_stations = process_station_data(SEM)
                            grid_components = process_grid_data(SEM)
                            

                            #Process the input grid of Vs
                            X_grid, Z_grid, Vs = grid_components['X_grid'], grid_components['Z_grid'], grid_components['Vs']
                            ZOI_mask = make_ZOI_mask(X_grid, Z_grid)
                            X_grid, Z_grid, Vs = X_grid[ZOI_mask], Z_grid[ZOI_mask], Vs[ZOI_mask]
                            X_lin = np.linspace(np.min(X_grid), np.max(X_grid), Nx)
                            Z_lin = np.linspace(np.min(Z_grid), np.max(Z_grid), Ny)
                            X, Z = np.meshgrid(X_lin, Z_lin)
                            soil_mask = (Z_grid < 0)
                            structure_mask = (np.abs(Z_grid) < 30) & (np.abs(X_grid) < 10)
                            points_soil = np.column_stack((X_grid[soil_mask], Z_grid[soil_mask]))
                            points_structure = np.column_stack((X_grid[structure_mask], Z_grid[structure_mask]))
                            Vs_soil = griddata(points_soil, Vs[soil_mask], (X,Z), method='linear')
                            Vs_structure = griddata(points_structure, Vs[structure_mask], (X,Z), method='linear')
                            Vs_soil = np.nan_to_num(Vs_soil, nan=0, posinf=0, neginf=0)
                            Vs_structure = np.nan_to_num(Vs_structure, nan=0, posinf=0, neginf=0)
                            Vs_grid = np.add(Vs_soil,Vs_structure)
                            # plt.imshow(Vs_grid, origin='lower', cmap='terrain')
                            # plt.colorbar()
                            # plt.show()

                            #Process the output data for fault displacement
                            X_glob = []
                            Z_glob = []
                            S1_glob = []
                            S2_glob = []
                            # len_fault = time_fault[:-1].size
                            len_fault = time_fault.size
                            offset = len_fault//Nt
                            for interf in ['Left', 'Bottom', 'Right']:
                                fault_dic = fault_components[interf]
                                X, Z= fault_dic['X_fault'], fault_dic['Z_fault']
                                Slip_1, Slip_2 = fault_dic['Slip_1'], fault_dic['Slip_2']
                                # ZOI_mask = make_ZOI_mask(X, Z)
                                # X, Z, Slip_1, Slip_2 = X[ZOI_mask], Z[ZOI_mask], Slip_1[ZOI_mask,:], Slip_2[ZOI_mask,:]
                                for i, x, z in zip(range(X.size), X, Z):
                                    s1 = Slip_1[i,::offset]
                                    s2 = Slip_2[i,::offset]
                                    s1 = s1[:-1]
                                    s2 = s2[:-1]
                                    X_glob.append(x), Z_glob.append(z), S1_glob.append(s1), S2_glob.append(s2)
                            Displacement_data = np.zeros([len(X_glob),2*Nt+2])
                            for i, x, z, s1, s2 in zip(range(len(X_glob)), X_glob, Z_glob, S1_glob, S2_glob):
                                Displacement_data[i,0] = x 
                                Displacement_data[i,1] = z
                                Displacement_data[i,2:] = np.concatenate([s1,s2], axis=0)

                            #Process the output data for velocities snapshots (A MODIFIER POUR LES SNAPSHOTS)
                            # X_sta, Z_sta = station_components['X_station'], station_components['Z_station']
                            # Vx, Vz = station_components['Vx'], station_components['Vz']
                            X_sta, Z_sta = station_components['X_snap'], station_components['Z_snap']
                            Vx, Vz = station_components['Vx_snap'], station_components['Vz_snap']
                            print(X_sta.shape)
                            print(Vx.shape)
                            ZOI_mask = make_ZOI_mask(X_sta, Z_sta)
                            # X_sta, Z_sta, Vx, Vz = X_sta[ZOI_mask], Z_sta[ZOI_mask], Vx[:,ZOI_mask], Vz[:, ZOI_mask]
                            X_sta, Z_sta, Vx, Vz = X_sta[ZOI_mask], Z_sta[ZOI_mask], Vx[ZOI_mask,:], Vz[ZOI_mask,:]
                            Vx_glob = []
                            Vz_glob = []
                            # len_station = time_stations[:-1].size
                            len_station = time_stations.size
                            offset = len_station//Nt
                            for i in range(X_sta.size):
                                Vx_i, Vz_i = Vx[i,::offset], Vz[i,::offset]
                                Vx_i, Vz_i = Vx_i[:-2], Vz_i[:-2]
                                Vx_glob.append(Vx_i)
                                Vz_glob.append(Vz_i)

                            Velocity_data = np.zeros([X_sta.size, 2*Nt+2])
                            for i, x, z, vx, vz in zip(range(X_sta.size), X_sta, Z_sta, Vx_glob, Vz_glob):
                                Velocity_data[i, 0] = x
                                Velocity_data[i, 1] = z 
                                Velocity_data[i, 2:] = np.concatenate([vx,vz], axis=0)
                                    
                                
                            # Export data
                            for p in ["/input_Vs", "/input_signal", "/input_angle", "/input_displacement", "/input_velocity"]:
                                try:
                                    os.mkdir(os.path.dirname(__file__)+p)
                                except FileExistsError:
                                    pass
                            np.save(os.path.dirname(__file__)+f'/input_Vs/Vs_case_{e:03d}.npy', Vs_grid)
                            np.save(os.path.dirname(__file__)+f'/input_signal/signal_case_{e:03d}.npy', station_components['V_input'])
                            np.save(os.path.dirname(__file__)+f'/input_angle/angle_case_{e:03d}.npy', angle)
                            np.save(os.path.dirname(__file__)+f'/input_displacement/displacement_case_{e:03d}.npy', Displacement_data)
                            np.save(os.path.dirname(__file__)+f'/input_velocity/velocity_case_{e:03d}.npy', Velocity_data)
                        e+=1
                    except Exception :
                        pass
                    


export_data()
