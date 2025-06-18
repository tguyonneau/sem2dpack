"""
This script generates an ISS input file for a 2D seismic wave propagation simulation.
It is not meant to be run directly, but rather to be imported in a batch generation script.
"""

import sys
sys.path.append("./PARAM_GENERATION/")
from Class import *
from Functions import *


# Create a new input file
ISS = Input(dir_output+'/Par.inp')

# Set general parameters
ISS.set_general_parameters(iexec=1, ngll=5, fmax=10., ndof=2, verbose='1111', ItInfo=10000)

# Build the mesh
mesh = Mesh('MESH2D', file='Mesh_ISS.mesh2d')
ISS.set_mesh(mesh)

# Set material properties
mat1 = Material(1, 'ELAST', rho=rho_1, cp=700., cs=300.)
mat2 = Material(2, 'ELAST', rho=rho_2, cp=700., cs=300.)
ISS.set_materials([mat1, mat2])

# Set boundary conditions
Absorb_1 = BC(1, 'ABSORB', Stacey=False, let_wave=True)
Absorb_2 = BC(2, 'ABSORB', Stacey=False, let_wave=True)
Absorb_4 = BC(1, 'ABSORB', Stacey=False, let_wave=True)
fric = Friction('SWF', Dc=1., MuS=0.3, MuD=0.3)
Fault_56 = BC((5, 6), 'DYNFLT', friction=fric, Sxx=-1., Sxz=0.3, otd=1e-5)
Fault_78 = BC((7, 8), 'DYNFLT', friction=fric, Sxx=-1., Sxz=0.3, otd=1e-5)
Fault_910 = BC((9, 10), 'DYNFLT', friction=fric, Sxx=-1., Sxz=0.3, otd=1e-5)
ISS.set_BC([Absorb_1, Absorb_2, Absorb_4, Fault_56, Fault_78, Fault_910])

# Set sources
stf_signal = STF('TAB', file='source')
mecha_signal = Mechanism('WAVE', angle=angle, phase='S')
source_signal = SRC(stf_signal, mecha_signal, (0., 0.))
stf_force = STF('TAB', file='weight_structure.inp')
mecha_force = Mechanism('FORCE', angle=0.)
source_force = SRC(stf_force, mecha_force, (0.,0.))
ISS.set_sources([source_signal, source_force])

# Set time scheme
ISS.set_time_scheme(TotalTime=TotalTime, dt=1e-5, courant=0.3, kind='leapfrog')

# Set receivers
interest_size = 30
X_left_interest,Z_left_interest = generate_stations_grid([-10.-interest_size, -10.], [-30., 0.], 2., 2.)
X_bottom_interest,Z_bottom_interest = generate_stations_grid([-10.-interest_size, 10.+interest_size], [-30.-interest_size, -30.], 2., 2.)
X_right_interest,Z_right_interest = generate_stations_grid([10., 10.+interest_size], [-30., 0.], 2., 2.)
X_left, Z_left = generate_stations_grid([-250, -10.-interest_size], [-30., 0.], 10., 4.)
X_bottom, Z_bottom = generate_stations_grid([-250, 250], [-100., 30.-interest_size], 10., 4.)
X_right, Z_right = generate_stations_grid([10.+interest_size,250], [-30., 0.], 10., 4.)
X_struct, Z_struct = generate_stations_grid([-10,10], [-30., 30.], 2., 2.)
X, Z = np.concatenate((X_left, X_bottom, X_right, X_left_interest, X_bottom_interest, X_right_interest)), np.concatenate((Z_left, Z_bottom, Z_right, Z_left_interest, Z_bottom_interest, Z_right_interest))
write_stations_file(dir_output+'/stations', X, Z)
ISS.set_receivers(file='stations', isamp=100, field='V', AtNode=False, extra=False)

# Set snapshot
ISS.set_snapshot(itd=20000, fields='V', components='xz', ps=False, bin=False)

