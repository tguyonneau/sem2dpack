import os
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import numpy as np
from scipy.interpolate import griddata

sys.path.append(os.path.dirname(__file__)+'/../../modules')
from Stage_module import *

SEM_grid = import_SEM_grid(os.path.dirname(__file__))
X = SEM_grid['X']
Z = SEM_grid['Z']
Vs = SEM_grid['Vs']

soil_mask = (Z <= 0)
structure_mask = (np.abs(Z) < 30) & (np.abs(X) < 10)

norm = colors.Normalize(np.min(Vs), np.max(Vs))
cmap = 'coolwarm'
SM = cm.ScalarMappable(norm=norm, cmap=cmap)
fig, ax = plt.subplots()
ax.tricontourf(X[soil_mask], Z[soil_mask], Vs[soil_mask], levels=50, cmap=cmap)
ax.tricontourf(X[structure_mask], Z[structure_mask], Vs[structure_mask], levels=50, cmap=cmap)
draw_example(ax)
ax.set_xlim([-250,250])
ax.set_ylim([-100,30])
fig.colorbar(SM, ax=ax)
ax.set_xlabel("X (m)")
ax.set_ylabel("Z (m)")
ax.set_title("S-Wave Velocity Profile")
plt.show()