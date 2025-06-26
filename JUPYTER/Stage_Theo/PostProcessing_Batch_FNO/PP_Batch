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
sys.path.append(os.path.dirname(__file__)+'/../')
sys.path.append(os.path.dirname(__file__)+'/../modules')

# Import custom modules
from Class_sem2dpack import *
from Stage_module import *
is_overburden = False
fmin, fmax = 0.01, 10.0
#----------------------------------------------------------------

L = [40, 200, 1000]
f = [0.5, 1, 2]
I = [0, 30]
N = 5
dataset_directory = "C:/Users/t.guyonneau/OneDrive - EGIS Group/Documents/OUTPUT/Dataset_1/"

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

def process_station_data_simplified(SEM):
    # Read the X component of stations data
    SEM.read_seismo('x')
    SEM.filter_seismo(fmin, fmax)
    Time_stations = SEM.time
    Vx = SEM.velocity[:,:]
    Ux = np.zeros(Vx.shape)
    Ax = np.zeros(Vx.shape)
    for i in range(Vx.shape[1]):
        V = Vx[:,i]
        Ux[:,i] = compute_displacement(V, Time_stations)
        Ax[:,i] = compute_acceleration(V, Time_stations)
        

    # Read the Z component of stations data
    SEM.read_seismo('z')
    SEM.filter_seismo(fmin, fmax)
    Vz = SEM.velocity[:,:]
    Uz = np.zeros(Vz.shape)
    Az = np.zeros(Vz.shape)
    for i in range(Vz.shape[1]):
        V = Vz[:,i]
        Uz[:,i] = compute_displacement(V, Time_stations)
        Az[:,i] = compute_acceleration(V, Time_stations)

    # Read Snapshots data
    for i in range(0,1000):
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

    # Compute PGV and PGA
    PGUx = np.max( np.max(np.abs(Ax), axis=0) ) #TEMPORAIRE : REMPLACER PAR LES SNAPSHOTS
    PGUz = np.max( np.max(np.abs(Az), axis=0) ) #TEMPORAIRE : REMPLACER PAR LES SNAPSHOTS
    PGVx = np.max( np.max(np.abs(Vx_snap), axis=1) )
    PGVz = np.max( np.max(np.abs(Vz_snap), axis=1) )
    PGAx = np.max( np.max(np.abs(Ax), axis=0) ) #TEMPORAIRE : REMPLACER PAR LES SNAPSHOTS
    PGAz = np.max( np.max(np.abs(Az), axis=0) ) #TEMPORAIRE : REMPLACER PAR LES SNAPSHOTS
    

    # Create a dictionary to hold the components of the stations data
    components = {}
    components['PGUx'] = PGUx
    components['PGUz'] = PGUz
    components['PGVx'] = PGVx
    components['PGVz'] = PGVz
    components['PGAx'] = PGAx
    components['PGAz'] = PGAz
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
    'PGUx': [],
    'PGUz': [],
    'PGVx': [],
    'PGVz': [],
    'PGAx': [],
    'PGAz': []
}

def generate_dataframe():
    for length in L:
        for frequency in f:
            for angle in I:
                for n in range(N):
                    direct = dataset_directory + f"Batch_L_{length:d}_f_{10*frequency:02.0f}_I_{angle:02.0f}/Run_{n:02d}"
                    SEM = sem2dpack(direct)
                    sim_components = {'Lc_x': length, 'f0': frequency, 'angle': angle}
                    fault_components = process_fault_data_simplified(SEM)
                    station_components = process_station_data_simplified(SEM)
                    combined_dic = sim_components | fault_components | station_components
                    for k in combined_dic.keys():
                        dictio[k].append(combined_dic[k])
    df = pd.DataFrame(dictio)
    return df


# df = generate_dataframe():
# df.to_csv(os.path.dirname(__file__)+'/'+os.path.basename(dataset_directory)+'.csv', index=False)

df = pd.read_csv(os.path.dirname(__file__)+'/Dataset_1.csv')


def scatter_plot(ax, X, Y, color_comp=None):
    if color_comp is None:
        ax.scatter(df[X], df[Y], label="Data points")
    else:
        for val in df[color_comp].unique():
            df_group = df[df[color_comp] == val]
            ax.scatter(df_group[X], df_group[Y], label=f"{color_comp} = {val}")
    ax.set_title(f"{X} vs {Y}")
    ax.set_xlabel(f"{X}")
    ax.set_ylabel(f"{Y}")

def polynomial_regression(ax, X, Y, n=1, on_each_subset=False, color_comp="Lc_x"):
    model = make_pipeline(PolynomialFeatures(degree=n), LinearRegression())
    if on_each_subset:
        if color_comp is None:
            raise Exception("Must precise a value for 'color_comp' or turn 'on_each_subset' to False")
        for val in df[color_comp].unique():
            df_group = df[df[color_comp] == val]
            X_sort, Y_sort = np.sort(df_group[X].to_numpy()), df_group[Y].to_numpy()[np.argsort(df_group[X].to_numpy())]
            model.fit(np.expand_dims(X_sort, axis=1), Y_sort)
            ax.plot(X_sort, model.predict(np.expand_dims(X_sort, axis=1)), ls='--', label=f"Fitting curve for {color_comp} = {val}")
    else:
        X_sort, Y_sort = np.sort(df[X]), df[Y][np.argsort(df[X])]
        model.fit(np.expand_dims(X_sort, axis=1), Y_sort)
        ax.plot(X_sort, model.predict(np.expand_dims(X_sort, axis=1)), ls='--', c='black', label="Fitting curve")


# fig, ax = plt.subplots()
# X = "PGVz"
# Y = "Peak_Sliding_Right"
# C = "f0"

# scatter_plot(ax, X, Y, color_comp=C)
# # polynomial_regression(ax, X, Y, on_each_subset=False, n=1, color_comp=C)
# ax.legend()
# # plt.show()

# df_small = df[['Peak_Sliding_Left', 'Peak_Uplift_Left', 'Peak_Sliding_Bottom', 'Peak_Uplift_Bottom', 'Peak_Sliding_Right', 'Peak_Uplift_Right', 'Lc_x']]
# pd.plotting.radviz(df_small, class_column='Lc_x')
# plt.show()



def double_color(ax, comp1, comp2, color_comp1, color_comp2):
    val1 = np.unique(df[color_comp1].to_numpy())
    val2 = np.unique(df[color_comp2].to_numpy())
    for v1 in val1:
        for v2 in val2:
            df1 = df[df[color_comp1]==v1]
            df2 = df1[df1[color_comp2]==v2]
            ax.scatter(df2[comp1], df2[comp2], label=f'{color_comp1}={v1} | {color_comp2}={v2}')
            ax.legend()
    ax.set_xlabel(comp1)
    ax.set_ylabel(comp2)
    ax.set_title(f"{comp2} VS {comp1}")

def triple_color(ax, comp1, comp2):
    val1 = np.unique(df["angle"].to_numpy())
    val2 = np.unique(df["f0"].to_numpy())
    val3 = np.unique(df["Lc_x"].to_numpy())
    for v1 in val1:
        for v2 in val2:
            for v3 in val3:
                df1 = df[df["angle"]==v1]
                df2 = df1[df1["f0"]==v2]
                df3 = df2[df2["Lc_x"]==v3]
                ax.scatter(df3[comp1], df3[comp2], label=f'angle={v1}° | f0={v2}Hz | Lc_x={v3}m', c=np.random.rand(1,3))
                ax.legend()
    ax.set_xlabel(comp1)
    ax.set_ylabel(comp2)
    ax.set_title(f"{comp2} VS {comp1}")



#-----------------------------------------

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance

# -------------------------------
# 🎯 Définition des paramètres et cibles
# -------------------------------
features = ["Lc_x", "f0", "angle"]  # Paramètres (variables explicatives)
targets = [
    'Peak_Sliding_Left', 'Peak_Uplift_Left',
    'Peak_Sliding_Bottom', 'Peak_Uplift_Bottom',
    'Peak_Sliding_Right', 'Peak_Uplift_Right',
    'PGVx', 'PGVz'
]  # Variables cibles à prédire

X = df[features]

# -------------------------------
# 🔁 Calcul de l’importance par permutation
# -------------------------------
importances_perm = {}

for target in targets:
    y = df[target]
    
    # Modèle de régression par forêt aléatoire
    model = RandomForestRegressor(n_estimators=100, random_state=0)
    model.fit(X, y)

    # Importance par permutation
    result = permutation_importance(
        model, X, y,
        n_repeats=200,
        random_state=0,
        scoring="r2"
    )
    
     # Importance brute
    importances = result.importances_mean

    # Normalisation : somme = 1
    importances_norm = importances / importances.sum()

    # Stocker l’importance normalisée
    importances_perm[target] = importances_norm

# -------------------------------
# 🔥 Affichage sous forme de heatmap
# -------------------------------
importances_df = pd.DataFrame(importances_perm, index=features)
# pd.plotting.radviz(importances_df, "Peak_Sliding_Left")
# print(importances_df)
# plt.figure(figsize=(10, 6))
# sns.heatmap(importances_df, annot=True, fmt=".3f", cmap="YlGnBu", cbar_kws={"label": "Importance"})
# plt.title("Importances normalisées des paramètres (Permutation Importance - Random Forest)")
# plt.xlabel("Variables cibles")
# plt.ylabel("Paramètres")
# plt.tight_layout()
# plt.show()

import ternary

# Préparer les points dans l’ordre (var1, var2, var3)
points = []
labels = []
for target, imp in importances_perm.items():
    normed = imp
    # On les convertit en pourcentage (sommant à 100)
    percent = [round(x * 100, 2) for x in normed]
    points.append(tuple(percent))
    labels.append(target)

# Initialiser le triangle
figure, tax = ternary.figure(scale=100)
tax.boundary()
tax.gridlines(multiple=10, color="gray")

# Ajouter les points
for point, label in zip(points, labels):
    tax.plot([point], marker='o', label=label, markersize=8)

# Légendes
tax.left_axis_label("angle", fontsize=12)
tax.right_axis_label("f0", fontsize=12)
tax.bottom_axis_label("Lc_x", fontsize=12)

tax.legend()
tax.set_title("Ternary Plot des Importances Normalisées", fontsize=14)
tax.ticks(axis='lbr', multiple=10)
tax.clear_matplotlib_ticks()
plt.tight_layout()
plt.show()