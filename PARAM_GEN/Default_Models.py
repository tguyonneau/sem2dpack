from Class import *
from Functions import *

def Generate_Prenolin_PSV(dir, xlim, zmin, TotalTime=10., dt=1e-5, nx=1, nx_station=1, nz_station=1, bin=False, itd=1000):
    Prenolin_PSV = Input(dir+"/Par.inp")
    #----- General ----------
    Prenolin_PSV.set_general_parameters(ndof=2, ItInfo=10000, ngll=5, iexec=1, fmax=10., verbose='1011')
    #----- Set mesh ---------
    mesh = Mesh(method='LAYERED')
    mesh.set_properties(xlim=xlim, zmin=zmin, nx=nx, file='layers')
    Prenolin_PSV.set_mesh(mesh)
    #----- Set source -------
    source = STF('TAB')
    source.set_properties(file='inputp1')
    #----- Set BC -----------
    BC1 = BC((2,4), kind='PERIOD')
    BC2 = BC(1, kind='DIRNEU')
    BC2.set_properties(h='N', v='N', hstf=source, vstf=source, borehole=True)
    Prenolin_PSV.set_BC([BC1,BC2])
    #----- Set time scheme --
    Prenolin_PSV.set_time_scheme(TotalTime=10., dt=1e-5, courant=0.3, kind='leapfrog')
    #Set receivers & snapshot
    X,Z=generate_stations_grid(xlim,[zmin,0],1,2)
    write_stations_file(dir+"/stations",X,Z)
    Prenolin_PSV.set_receivers(file='stations', isamp=20, field='V', AtNode=False, extra=True)
    Prenolin_PSV.set_snapshot(itd=itd, fields='V', components='xz', ps=False, bin=bin)
    return Prenolin_PSV