from Class import *
from Functions import *
from Default_Models import * 
from Soil_Models import * 


dir = "./PARAM_GEN/Test_Preno"
mat_list, layers = Volvi()
xlim = [-5,5]
zmin = -(np.sum(layers))
Preno = Generate_Prenolin_PSV(dir, xlim, zmin, TotalTime=3., nz_station=3)
Preno.set_materials(mat_list)
write_layers_file(dir+'/layers', layers, 10*np.ones(layers.size))
Preno.write_file()