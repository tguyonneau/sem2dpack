#import libraries
import sys
import os
import numpy as np
import time
# import matplotlib.pyplot as plt
# import matplotlib.animation as anim
# from matplotlib.cm import ScalarMappable
# from matplotlib.colors import Normalize
# from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
from scipy.optimize import curve_fit
import pandas as pd
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.pipeline import make_pipeline

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
dataset_directory = "../02_OUTPUT/Dataset30/"

#-------------------------------------------------------------


def process_fault_data_simplified(SEM):
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
        Slip_1 = data['Slip_1']
        Slip_2 = data['Slip_2']
        Peak_Sliding = np.max( np.max(np.abs(Slip_1), axis=1) )
        Peak_Uplift = np.max( np.max(np.abs(Slip_2), axis=1) )
        fault_components[key] = {
            'Peak_Sliding': Peak_Sliding,
            'Peak_Uplift': Peak_Uplift
            }
    fault_dic = {
        'Peak_Sliding_Left': fault_components['Left']['Peak_Sliding'],
        'Peak_Uplift_Left': fault_components['Left']['Peak_Uplift'],
        'Peak_Sliding_Bottom': fault_components['Bottom']['Peak_Sliding'],
        'Peak_Uplift_Bottom': fault_components['Bottom']['Peak_Uplift'],
        'Peak_Sliding_Right': fault_components['Right']['Peak_Sliding'],
        'Peak_Uplift_Right': fault_components['Right']['Peak_Uplift'],
    }
    return fault_dic

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

# Konno-Ohmachi smoothening
# Credit: Fabian Bonilla's library :)
def ko(datain,dx=None,bexp=None):
    from math import pi, log10, sin
    y = datain.copy()
    
    nx      = len(y)
    fratio  = 10.0**(2.5/bexp)
    ylis    = np.zeros(nx) #np.arange( nx )
    ylis[0] = y[0]

    for ix in np.arange( 1,nx ):
        fc  = float(ix)*dx
        fc1 = fc/fratio
        fc2 = fc*fratio
        ix1 = int(fc1/dx)
        ix2 = int(fc2/dx) + 1
        if ix1 <= 0:  ix1 = 1
        if ix2 >= nx: ix2 = nx
        a1 = 0.0
        a2 = 0.0
        for j in np.arange( ix1,ix2 ):
            if j != ix:
                c1 = bexp* np.log10(float(j)* dx/ fc)
                c1 = (sin(c1)/c1)**4
                a2 = a2+c1
                a1 = a1+c1*y[j]
            else:
                a2 = a2+1.0
                a1 = a1+y[ix]
        ylis[ix] = a1 / a2

    for ix in np.arange( nx ):
        y[ix] = ylis[ix]
    return y
###

# Computing the fft of the data
def get_FFT(dt=None, data=None):    
    from scipy.fftpack import fft
    # Spectrum    
    df=1.0/ dt
    N = len(data)
    f = np.linspace(0.0, 1.0/(2.0*dt), N//2)
    spec = abs(fft(data))* dt    
    return f[1:], spec[:int(N/2)-1]

def process_station_data_simplified(SEM):
    # Read Input Signal
    input_signal_path = SEM.directory+'/source'
    input_signal = np.genfromtxt(open(input_signal_path,'r'))
    time_input = input_signal[:,0]
    V_input = input_signal[:,1]
    U_input = compute_displacement(V_input.T, time_input).T
    A_input = compute_acceleration(V_input, time_input)
    PGD_input = np.max(np.abs(U_input))
    PGV_input = np.max(np.abs(V_input))
    PGA_input = np.max(np.abs(A_input))

    # Read the X component of stations data
    SEM.read_seismo('x')
    SEM.filter_seismo(fmin, fmax)
    Time_stations = SEM.time
    Vx = SEM.velocity[:,:]
    Ux = compute_displacement(Vx.T, Time_stations).T
    Ax = compute_acceleration(Vx.T, Time_stations).T
        

    # Read the Z component of stations data
    SEM.read_seismo('z')
    SEM.filter_seismo(fmin, fmax)
    Vz = SEM.velocity[:,:]
    Uz = compute_displacement(Vz.T, Time_stations).T
    Az = compute_acceleration(Vz.T, Time_stations).T

    # Read stations coordinates
    XSTA, ZSTA = SEM.rcoord[:,0], SEM.rcoord[:,1]

    Vx_list = []
    Vz_list = []
    valid_indices = []
    Time_stations = SEM.time
    # Lecture des snapshots disponibles
    for i in range(Time_stations.size):
        try:
            _, _, Vx_i = load_field(SEM, 'x', i)
            _, _, Vz_i = load_field(SEM, 'z', i)
            Vx_list.append(Vx_i)
            Vz_list.append(Vz_i)
            valid_indices.append(i)
        except FileNotFoundError:
            break  # Arrêt si un fichier est manquant

    # Vérifie qu’on a bien lu au moins un snapshot
    if len(Vx_list) == 0:
        raise RuntimeError("Aucun snapshot lu. Vérifiez les fichiers disponibles.")

    # Empilement vectorisé : shape finale = (nx | nz, nt)
    Vx_snap = np.stack(Vx_list, axis=-1)
    Vz_snap = np.stack(Vz_list, axis=-1)

    # Récupération des coordonnées (à partir du premier snapshot valide)
    X_snap, Z_snap, _ = load_field(SEM, 'x', valid_indices[0])

    # Compute displacement and acceleration for all snapshots
    Ux_snap = compute_displacement(Vx_snap, Time_stations[:-1])
    Uz_snap = compute_displacement(Vz_snap, Time_stations[:-1])
    Ax_snap = compute_acceleration(Vx_snap, Time_stations[:-1])
    Az_snap = compute_acceleration(Vz_snap, Time_stations[:-1])

    # Compute PGV and PGA
    PGDx = np.max(np.abs(Ux_snap), axis=1)
    PGDz = np.max(np.abs(Uz_snap), axis=1) 
    PGVx = np.max(np.abs(Vx_snap), axis=1)
    PGVz = np.max(np.abs(Vz_snap), axis=1)
    PGAx = np.max(np.abs(Ax_snap), axis=1)
    PGAz = np.max(np.abs(Az_snap), axis=1)

    # Differentiate between soil and structure
    structure_mask = (np.abs(X_snap) < 10) & (np.abs(Z_snap) < 30)
    soil_mask = ~structure_mask
    PGDx_soil = np.max(PGDx[soil_mask])
    PGDz_soil = np.max(PGDz[soil_mask])
    PGVx_soil = np.max(PGVx[soil_mask])
    PGVz_soil = np.max(PGVz[soil_mask])
    PGAx_soil = np.max(PGAx[soil_mask])
    PGAz_soil = np.max(PGAz[soil_mask])
    PGDx_structure = np.max(PGDx[structure_mask])
    PGDz_structure = np.max(PGDz[structure_mask])
    PGVx_structure = np.max(PGVx[structure_mask])
    PGVz_structure = np.max(PGVz[structure_mask])
    PGAx_structure = np.max(PGAx[structure_mask])
    PGAz_structure = np.max(PGAz[structure_mask])


    # FFT at surface station
    s = get_nearest_station(30, 0, XSTA, ZSTA)
    V_sta = Vx[:, s]
    dt_input = time_input[1] - time_input[0]
    dt_sta = Time_stations[1] - Time_stations[0]

    # Zero-padding to common length
    n_input = len(V_input)
    n_sta = len(V_sta)
    n_fft = 2**int(np.ceil(np.log2(max(n_input, n_sta))))  # next power of 2

    # Pad both signals to same length
    V_input_pad = np.pad(V_input, (0, n_fft - n_input), mode='constant')
    V_sta_pad = np.pad(V_sta, (0, n_fft - n_sta), mode='constant')

    # Compute FFTs
    # FFT_input, freq_input = fourier(V_input_pad, dt_input)
    # FFT_sta, freq_sta = fourier(V_sta_pad, dt_sta)
    freq_input, FFT_input = get_FFT(dt_input, V_input_pad)
    freq_sta, FFT_sta = get_FFT(dt_sta, V_sta_pad)

    epsilon = 1e-5  # Small value to avoid division by zero
    bexp = 25       # Smoothing factor for Konno-Ohmachi smoothing

    # Apply Konno-Ohmachi smoothing
    FFT_input_smooth = ko(FFT_input, dx=freq_input[1] - freq_input[0], bexp=bexp)
    FFT_sta_smooth = ko(FFT_sta, dx=freq_sta[1] - freq_sta[0], bexp=bexp)

    # Ensure same frequency axis for TF computation (they now should match)
    TF = FFT_sta_smooth / np.maximum(FFT_input_smooth, epsilon * np.ones_like(FFT_input_smooth))
    
    
    # Create a dictionary to hold the components of the stations data
    components = {}

    # components['time_input'] = time_input
    # components['U_input'] = U_input
    # components['V_input'] = V_input
    # components['A_input'] = A_input

    # components['X'] = XSTA
    # components['Z'] = ZSTA
    # components['Ux'] = Ux
    # components['Uz'] = Uz
    # components['Vx'] = Vx
    # components['Vz'] = Vz
    # components['Ax'] = Ax
    # components['Az'] = Az

    # components['X_snap'] = X_snap
    # components['Z_snap'] = Z_snap
    # components['Ux_snap'] = Ux_snap
    # components['Uz_snap'] = Uz_snap
    # components['Vx_snap'] = Vx_snap
    # components['Vz_snap'] = Vz_snap
    # components['Ax_snap'] = Ax_snap
    # components['Az_snap'] = Az_snap
    
    # components['PGDx'] = PGDx
    # components['PGDz'] = PGDz
    # components['PGVx'] = PGVx
    # components['PGVz'] = PGVz
    # components['PGAx'] = PGAx
    # components['PGAz'] = PGAz

    # components['FFT_input'] = FFT_input_smooth
    # components['FFT_sta'] = FFT_sta_smooth
    # components['TF'] = TF
    # components['freq_input'] = freq_input
    # components['freq_sta'] = freq_sta

    components['PGD_input'] = PGD_input
    components['PGV_input'] = PGV_input
    components['PGA_input'] = PGA_input
    components['PGDx_soil'] = PGDx_soil    
    components['PGDz_soil'] = PGDz_soil
    components['PGVx_soil'] = PGVx_soil
    components['PGVz_soil'] = PGVz_soil
    components['PGAx_soil'] = PGAx_soil
    components['PGAz_soil'] = PGAz_soil
    components['PGDx_structure'] = PGDx_structure
    components['PGDz_structure'] = PGDz_structure
    components['PGVx_structure'] = PGVx_structure
    components['PGVz_structure'] = PGVz_structure
    components['PGAx_structure'] = PGAx_structure
    components['PGAz_structure'] = PGAz_structure
    components['TF'] = TF
    components['freq'] = freq_input

    return components

dictio = {
    'Lc_x': [],
    'f0': [],
    'angle': [],
    'Peak_Sliding_Left': [],
    'Peak_Uplift_Left': [],
    'Peak_Sliding_Bottom': [],
    'Peak_Uplift_Bottom': [],
    'Peak_Sliding_Right': [],
    'Peak_Uplift_Right': [],
    'PGD_input': [],
    'PGV_input': [],
    'PGA_input': [],
    'PGDx_soil': [],
    'PGDz_soil': [],
    'PGVx_soil': [],
    'PGVz_soil': [],
    'PGAx_soil': [],
    'PGAz_soil': [],
    'PGDx_structure': [],
    'PGDz_structure': [],
    'PGVx_structure': [],
    'PGVz_structure': [],
    'PGAx_structure': [],
    'PGAz_structure': []
}

def generate_dataframe():
    numb=0
    for length in L:
        for frequency in f:
            for angle in I:
                for n in range(N):
                    direct = dataset_directory + f"Batch_L_{length:d}_f_{10*frequency:02.0f}_I_{angle:02.0f}/Run_{n:02d}"
                    try:
                        start = time.time()
                        SEM = sem2dpack(direct)
                        sim_components = {'Lc_x': length, 'f0': frequency, 'angle': angle}
                        fault_components = process_fault_data_simplified(SEM)
                        station_components = process_station_data_simplified(SEM)
                        # print(type(sim_components))
                        # print(type(fault_components))
                        # print(type(station_components))

                        combined_dic = {**sim_components, **fault_components, **station_components}
                        for k in combined_dic.keys():
                            dictio[k].append(combined_dic[k])

                        TF = station_components['TF']
                        freq = station_components['freq']
                        np.save(f'./TF/TF{numb:03d}.npy', TF)
                        np.save(f'./TF/freq{numb:03d}.npy', freq)
                        stop = time.time()
                        print(f"Iteration time = {stop-start:.2f}s")
                        numb = numb+1
                    except Exception as e:
                        print(f"An Exception {e} as occured")
                        pass
    df = pd.DataFrame(dictio)
    return df


df = generate_dataframe()
#print(os.path.basename(dataset_directory[:-1]))
df.to_csv('./'+os.path.basename(dataset_directory[:-1])+'.csv', index=False)

# df = pd.read_csv(os.path.dirname(__file__)+'/Dataset_1.csv')


# def scatter_plot(ax, X, Y, color_comp=None):
#     if color_comp is None:
#         ax.scatter(df[X], df[Y], label="Data points")
#     else:
#         for val in df[color_comp].unique():
#             df_group = df[df[color_comp] == val]
#             ax.scatter(df_group[X], df_group[Y], label=f"{color_comp} = {val}")
#     ax.set_title(f"{X} vs {Y}")
#     ax.set_xlabel(f"{X}")
#     ax.set_ylabel(f"{Y}")

# def polynomial_regression(ax, X, Y, n=1, on_each_subset=False, color_comp="Lc_x"):
#     model = make_pipeline(PolynomialFeatures(degree=n), LinearRegression())
#     if on_each_subset:
#         if color_comp is None:
#             raise Exception("Must precise a value for 'color_comp' or turn 'on_each_subset' to False")
#         for val in df[color_comp].unique():
#             df_group = df[df[color_comp] == val]
#             X_sort, Y_sort = np.sort(df_group[X].to_numpy()), df_group[Y].to_numpy()[np.argsort(df_group[X].to_numpy())]
#             model.fit(np.expand_dims(X_sort, axis=1), Y_sort)
#             ax.plot(X_sort, model.predict(np.expand_dims(X_sort, axis=1)), ls='--', label=f"Fitting curve for {color_comp} = {val}")
#     else:
#         X_sort, Y_sort = np.sort(df[X]), df[Y][np.argsort(df[X])]
#         model.fit(np.expand_dims(X_sort, axis=1), Y_sort)
#         ax.plot(X_sort, model.predict(np.expand_dims(X_sort, axis=1)), ls='--', c='black', label="Fitting curve")


# # fig, ax = plt.subplots()
# # X = "PGVz"
# # Y = "Peak_Sliding_Right"
# # C = "f0"

# # scatter_plot(ax, X, Y, color_comp=C)
# # # polynomial_regression(ax, X, Y, on_each_subset=False, n=1, color_comp=C)
# # ax.legend()
# # # plt.show()

# # df_small = df[['Peak_Sliding_Left', 'Peak_Uplift_Left', 'Peak_Sliding_Bottom', 'Peak_Uplift_Bottom', 'Peak_Sliding_Right', 'Peak_Uplift_Right', 'Lc_x']]
# # pd.plotting.radviz(df_small, class_column='Lc_x')
# # plt.show()



# def double_color(ax, comp1, comp2, color_comp1, color_comp2):
#     val1 = np.unique(df[color_comp1].to_numpy())
#     val2 = np.unique(df[color_comp2].to_numpy())
#     for v1 in val1:
#         for v2 in val2:
#             df1 = df[df[color_comp1]==v1]
#             df2 = df1[df1[color_comp2]==v2]
#             ax.scatter(df2[comp1], df2[comp2], label=f'{color_comp1}={v1} | {color_comp2}={v2}')
#             ax.legend()
#     ax.set_xlabel(comp1)
#     ax.set_ylabel(comp2)
#     ax.set_title(f"{comp2} VS {comp1}")

# def triple_color(ax, comp1, comp2):
#     val1 = np.unique(df["angle"].to_numpy())
#     val2 = np.unique(df["f0"].to_numpy())
#     val3 = np.unique(df["Lc_x"].to_numpy())
#     for v1 in val1:
#         for v2 in val2:
#             for v3 in val3:
#                 df1 = df[df["angle"]==v1]
#                 df2 = df1[df1["f0"]==v2]
#                 df3 = df2[df2["Lc_x"]==v3]
#                 ax.scatter(df3[comp1], df3[comp2], label=f'angle={v1}° | f0={v2}Hz | Lc_x={v3}m', c=np.random.rand(1,3))
#                 ax.legend()
#     ax.set_xlabel(comp1)
#     ax.set_ylabel(comp2)
#     ax.set_title(f"{comp2} VS {comp1}")



# #-----------------------------------------

# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.inspection import permutation_importance

# # -------------------------------
# # 🎯 Définition des paramètres et cibles
# # -------------------------------
# features = ["Lc_x", "f0", "angle"]  # Paramètres (variables explicatives)
# targets = [
#     'Peak_Sliding_Left', 'Peak_Uplift_Left',
#     'Peak_Sliding_Bottom', 'Peak_Uplift_Bottom',
#     'Peak_Sliding_Right', 'Peak_Uplift_Right',
#     'PGVx', 'PGVz'
# ]  # Variables cibles à prédire

# X = df[features]

# # -------------------------------
# # 🔁 Calcul de l’importance par permutation
# # -------------------------------
# importances_perm = {}

# for target in targets:
#     y = df[target]
    
#     # Modèle de régression par forêt aléatoire
#     model = RandomForestRegressor(n_estimators=100, random_state=0)
#     model.fit(X, y)

#     # Importance par permutation
#     result = permutation_importance(
#         model, X, y,
#         n_repeats=200,
#         random_state=0,
#         scoring="r2"
#     )
    
#      # Importance brute
#     importances = result.importances_mean

#     # Normalisation : somme = 1
#     importances_norm = importances / importances.sum()

#     # Stocker l’importance normalisée
#     importances_perm[target] = importances_norm

# # -------------------------------
# # 🔥 Affichage sous forme de heatmap
# # -------------------------------
# importances_df = pd.DataFrame(importances_perm, index=features)
# # pd.plotting.radviz(importances_df, "Peak_Sliding_Left")
# # print(importances_df)
# # plt.figure(figsize=(10, 6))
# # sns.heatmap(importances_df, annot=True, fmt=".3f", cmap="YlGnBu", cbar_kws={"label": "Importance"})
# # plt.title("Importances normalisées des paramètres (Permutation Importance - Random Forest)")
# # plt.xlabel("Variables cibles")
# # plt.ylabel("Paramètres")
# # plt.tight_layout()
# # plt.show()

# import ternary

# # Préparer les points dans l’ordre (var1, var2, var3)
# points = []
# labels = []
# for target, imp in importances_perm.items():
#     normed = imp
#     # On les convertit en pourcentage (sommant à 100)
#     percent = [round(x * 100, 2) for x in normed]
#     points.append(tuple(percent))
#     labels.append(target)

# # Initialiser le triangle
# figure, tax = ternary.figure(scale=100)
# tax.boundary()
# tax.gridlines(multiple=10, color="gray")

# # Ajouter les points
# for point, label in zip(points, labels):
#     tax.plot([point], marker='o', label=label, markersize=8)

# # Légendes
# tax.left_axis_label("angle", fontsize=12)
# tax.right_axis_label("f0", fontsize=12)
# tax.bottom_axis_label("Lc_x", fontsize=12)

# tax.legend()
# tax.set_title("Ternary Plot des Importances Normalisées", fontsize=14)
# tax.ticks(axis='lbr', multiple=10)
# tax.clear_matplotlib_ticks()
# plt.tight_layout()
# plt.show()
