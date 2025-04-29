import sys
from Class import *
#sys.path.append('./PARA_GEN')
from Functions import *

#Create the Input file
Para = Input("./PARAM_GEN/Prenolin_Multicouche/Par.inp")

#Set general parameters
Para.set_general_parameters(ndof=2, ItInfo=10000, ngll=5, iexec=1, fmax=10., verbose='1011')

#Set mesh
mesh = Mesh(method='LAYERED')
mesh.set_properties(xlim=(0.,5.), zmin=-50., nx=1, file='layers')
Para.set_mesh(mesh)

#Set source
source = STF('TAB')
source.set_properties(file='inputp1')

#Set BC
BC1 = BC((2,4), kind='PERIOD')
BC2 = BC(1, kind='DIRNEU')
BC2.set_properties(h='N', v='N', hstf=source, vstf=source, borehole=True)
Para.set_BC([BC1,BC2])

#Set materials

mat1 = Material(1, 'ELAST')
mat1.set_properties(rho=2000., cp=700., cs=300.)
mat2 = Material(2, 'ELAST')
mat2.set_properties(rho=2000., cp=2*700., cs=2*300.)
mat3 = Material(3, 'ELAST')
mat3.set_properties(rho=2000., cp=3*700., cs=3*300.)
mat4 = Material(4, 'ELAST')
mat4.set_properties(rho=2000., cp=4*700., cs=4*300.)
mat5 = Material(5, 'ELAST')
mat5.set_properties(rho=2000., cp=5*700., cs=5*300.)

Para.set_materials([mat1,mat2,mat3,mat4,mat5])

#Layers file
file = open("./PARAM_GEN/Prenolin_Multicouche/layers",'w+')
for i in range(5):
    file.write(f"{-10*i}d0\t10\t{i+1}\n")
file.close()

#Set time scheme
Para.set_time_scheme(TotalTime=10., dt=1e-5, courant=0.3, kind='leapfrog')

#Set receivers & snapshot
X,Z=generate_stations_grid([0,5],[-50,0],1,2)
write_stations_file("./PARAM_GEN/Prenolin_Multicouche/stations",X,Z)
Para.set_receivers(file='stations', isamp=20, field='V', AtNode=True, extra=True)
Para.set_snapshot(itd=1000, fields='V', components='xz', ps=False, bin=False)

#Create file
Para.write_file()