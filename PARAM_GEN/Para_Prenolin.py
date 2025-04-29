from Class import *
from Functions import *
from Default_Models import * 

dir = "./PARAM_GEN/Test_Preno"
xlim = [-5,5]
zmin = -50
Preno = Generate_Prenolin_PSV(dir, xlim, zmin, TotalTime=3, nz_station=2.5)

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

Preno.set_materials([mat1,mat2,mat3,mat4,mat5])

#Layers file
file = open("./PARAM_GEN/Prenolin_Multicouche/layers",'w+')
for i in range(5):
    file.write(f"{-10*i}d0\t10\t{i+1}\n")
file.close()


#Create file
Preno.write_file()