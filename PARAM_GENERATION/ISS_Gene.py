from Class import *
from Functions import *


# Create a new input file
ISS = Input(direct+'/Par.inp')

# Set general parameters
ISS.set_general_parameters(iexec=1, ngll=5, fmax=10., ndof=2, verbose='1111', ItInfo=10000)

# Build the mesh
mesh = Mesh('MESH2D', file='test_v8.mesh2d')
ISS.set_mesh(mesh)

# Set material properties
mat1 = Material(1, 'ELAST', rho=2000., cp=700., cs=300.)
mat2 = Material(2, 'ELAST', rho=2000., cp=700., cs=300.)
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
gauss = STF('GAUSSIAN', ampli=0.1, f0=1., onset=0.7)
mecha = Mechanism('WAVE', angle=-30., phase='S')
source = SRC(gauss, mecha, (0., 0.))
ISS.set_sources([source])

# Set time scheme
ISS.set_time_scheme(TotalTime=5., dt=1e-5, courant=0.3, kind='leapfrog')

# Set receivers
X_left,Z_left = generate_stations_grid([-15., -10.], [-30., 0.], 1., 3.)
X_bottom,Z_bottom = generate_stations_grid([-10., 10.], [-35., -30.], 1., 3.)
X_right,Z_right = generate_stations_grid([10., 15.], [-30., 0.], 1., 3.)
X, Z = np.concatenate((X_left, X_bottom, X_right)), np.concatenate((Z_left, Z_bottom, Z_right))
write_stations_file(direct+'/stations', X, Z)
ISS.set_receivers(file='stations', isamp=20, field='V', AtNode=False, extra=False)

# Set snapshot
ISS.set_snapshot(itd=10000, fields='V', components='xz', ps=False)

#Write the file
ISS.write_file()