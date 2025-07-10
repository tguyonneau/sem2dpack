import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import pandas as pd
from houches_fb import *
#from scipy.integrate import cumulative_simpson
# from scipy.differentiate import derivative




def read_fault_testing(self, ff=np.float32, LENTAG=1, is_rate_and_state=False, ftag=None):
    #Definition of a fault data reading function
    from distutils import util
    
    ''' Script to read FltXX files.
    Assuming that a single boundary output has been defined for the fault.
    to modify later for multiple fault boundaries...
    , also to modify for files with data > 5.'''

    BC = []; fault = {}
    found = False
    if ftag == None:
        for n, f in enumerate([self.directory+'/Flt'+('%02d' % i)+'_sem2d.hdr' for i in np.arange(1,15)]):
            found = os.path.exists(f)
            print (i, found)
            if found :
                BC.append(n+1)
                print ('Fault boundary: ', BC)
            ##
        ##
    else:
        f = self.directory+'/Flt'+('%02d' % ftag)+'_sem2d.hdr'
        found = os.path.exists(f)
    if found: BC.append(ftag)          
    ##

    if not found : 
        print ('No Flt .hdr file found!')
        return
    ##
    elif not is_rate_and_state:     
        print ('DEBUG :: BC', BC, found)
        # Header file
        fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_sem2d.hdr'
        data = pd.read_csv(fname, names=('npts','ndat','nsamp','delta'), sep=r'\s+', header=0, nrows=1)
        fault['npts'] = data['npts'].values[0]
        fault['ndat'] = data['ndat'].values[0]
        fault['nsamp'] = data['nsamp'].values[0]
        fault['delta'] = data['delta'].values[0]
        with open(fname, 'r') as f:
            line  = f.readlines()[2:3][0]
            fault['dat_names'] =  [el.replace('\n','').replace(' ','') for el in line.split(':')]
        data = pd.read_csv(fname, names=('x','z'), sep=r'\s+' , header=3)
        fault['x'] = data['x'].values
        fault['z'] = data['z'].values        

        # Init file
        fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_init_sem2d.tab'
        if os.path.exists(fname):
            data = pd.read_csv(fname, names=('st0','sn0','mu0'), sep=r'\s+', header=None)
            fault['st0'] = data['st0'].values
            fault['sn0'] = data['sn0'].values
            fault['mu0'] = data['mu0'].values

        # Read fault data in a big matrix
        fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_sem2d.dat'
        if os.path.exists(fname):
            with open(fname, 'rb') as fid:
                whole = np.fromfile(fid, ff) 
                # BUG : nsamp is not correct inside the code !
                try:
                    array = whole.reshape((2*LENTAG+fault['npts'], fault['ndat'], fault['nsamp']), order='F')
                except:
                    fault['nsamp'] -=1
                    array = whole.reshape((2*LENTAG+fault['npts'], fault['ndat'], fault['nsamp']), order='F')

                for j in np.arange(fault['ndat']):
                    print ('Assigning ', fault['dat_names'][j])
                    dat = fault['dat_names'][j]
                    data = array[LENTAG:LENTAG+fault['npts'], j, :]
                    fault [dat] = data
        fault['Time'] = np.linspace(0.0, fault['delta']* (fault['nsamp']), num=fault['nsamp'])

    elif is_rate_and_state:
        
        # Header file
        fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_sem2d.hdr'
        data = pd.read_csv(fname, names=('npts','ndat'), sep=r'\s+', header=0, nrows=1)
        fault['npts'] = data['npts'].values[0]
        fault['ndat'] = data['ndat'].values[0]    
        with open(fname, 'r') as f:
            line  = f.readlines()[2:3][0]
            fault['dat_names'] =  [el.replace('\n','').replace(' ','') for el in line.split(':')]        
        data = pd.read_csv(fname, names=('x','z'), sep=r'\s+', header=3)
        fault['x'] = data['x'].values
        fault['z'] = data['z'].values         
        
        # Init file
        fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_init_sem2d.tab'
        if os.path.exists(fname):
            fault['st0'] = np.genfromtxt(fname, usecols=0)
            fault['sn0'] = np.genfromtxt(fname, usecols=1)
            fault['mu0'] = np.genfromtxt(fname, usecols=2)
            fault['theta0'] = np.genfromtxt(fname, usecols=3)
            fault['V0'] = np.genfromtxt(fname, usecols=4)            
            fault['a'] = np.genfromtxt(fname, usecols=5)
            fault['b'] = np.genfromtxt(fname, usecols=6)
        
    
        # Data file I
        # Read fault data in a big matrix
        fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_sem2d.dat'
        if os.path.exists(fname):
            with open(fname, 'rb') as fid:
                whole = np.fromfile(fid, ff) 
                
                nsamp = len(whole)/(2*LENTAG+fault['npts'])/fault['ndat']
                print ('Guessed array size, nsamp: ', nsamp)
                fault['nsamp'] = int(nsamp)
                
                array = whole.reshape((2*LENTAG+fault['npts'], fault['ndat'], fault['nsamp']), order='F')
                
                for j in np.arange(fault['ndat']):
                    print ('Assigning ', fault['dat_names'][j])
                    dat = fault['dat_names'][j]
                    data = array[LENTAG:LENTAG+fault['npts'], j, :]
                    fault[dat] = data                    
                
                
        # Data file II 
        # Read fault data in a big matrix
        fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_time_sem2d.tab'        
        if os.path.exists(fname):
            print(fname)
            fault['it'] = np.genfromtxt(fname, usecols=0)
            fault['dt'] = np.genfromtxt(fname, usecols=1)
            fault['t'] = np.genfromtxt(fname, usecols=2)
            fault['#EQ'] = np.genfromtxt(fname, usecols=3)
            dum = np.genfromtxt(fname, usecols=4, dtype=str)
            fault['isDyn'] = np.array( [bool(util.strtobool(d)) for d in dum] )             
            dum = np.genfromtxt(fname, usecols=5, dtype=str)
            fault['isSwitch'] = np.array( [bool(util.strtobool(d)) for d in dum] )
            dum = np.genfromtxt(fname, usecols=6, dtype=str)
            fault['isEq'] = np.array( [bool(util.strtobool(d)) for d in dum] )      

        # EDIT 02/07/25 : No use for potency files

        # # Data file III
        # # Read potency and potency rate, currently only for out-of-plane (ndof=1)
        # # for in-plane models change usecols and potency* arrays' size
        # fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_potency_sem2d.tab'        
        # if os.path.exists(fname):
        #     print(fname)
        #     # POTENCY
        #     # out-of plane model -- compo 13
        #     # replace D by e for python 
        #     array = np.genfromtxt(fname,usecols=0, dtype=None,  encoding=None)
        #     array_fixed  = np.array( [float(dum.replace('D','e')) for dum in array])
        #     fault['potency'] = np.zeros((array_fixed.shape[0], 2))
        #     fault['potency_rate'] = np.zeros((array_fixed.shape[0], 2))    
        #     fault['potency'][:,0] = array_fixed
            
        #     # out-of plane model -- compo 23
        #     array = np.genfromtxt(fname,usecols=1, dtype=None,  encoding=None)
        #     array_fixed  = np.array( [float(dum.replace('D','e')) for dum in array])    
        #     fault['potency'][:,1] = array_fixed
            
        #     # POTENCY RATE
        #     # out-of plane model -- compo 13
        #     array = np.genfromtxt(fname,usecols=2, dtype=None,  encoding=None)
        #     array_fixed  = np.array( [float(dum.replace('D','e')) for dum in array])    
        #     fault['potency_rate'][:,0] = array_fixed
                
        #     # out-of plane model -- compo 23
        #     array = np.genfromtxt(fname,usecols=3, dtype=None,  encoding=None)
        #     array_fixed  = np.array( [float(dum.replace('D','e')) for dum in array])    
        #     fault['potency_rate'][:,1] = array_fixed    

    self.fault = fault        

    # Find the earthquake
    if is_rate_and_state:
        cdt_beg = (self.fault['isDyn']==True) & (np.roll(self.fault['isDyn'], 1)==False)
        cdt_end = (self.fault['isDyn']==True) & (np.roll(self.fault['isDyn'], -1)==False)
        index = np.arange(0, len(self.fault['isDyn']))
        print ('Number of dynamic beginning and ending points:', len(index[cdt_beg]), len(index[cdt_end]))   
    ##
    return
###


def sem2d_read_fault(model_name,fault_name):
    
    # length of the tag at the begining and end of a binary record
    # in number of single precision words (4*bytes)
    LENTAG = 2; # gfortran older versions
    LENTAG = 1;
    
    # assumes header file name is FltXX_sem2d.hdr
    if not os.path.isdir(model_name):
        print("Wrong path to the model directory...")
        exit()
    headfile_exist = os.path.isfile(model_name+"/"+fault_name+"_sem2d.hdr")
    initfile_exist = os.path.isfile(model_name+"/"+fault_name+"_init_sem2d.tab")
    datafile_exist = os.path.isfile(model_name+"/"+fault_name+"_sem2d.dat")
    if (not headfile_exist):
        print("Miss head file in this directory...")
        exit()
    elif (not initfile_exist):
        print("Miss init file in this directory...")
        exit()
    elif (not datafile_exist):
        print("Miss fault data files in this directory...")
        exit()
    
    data = {}
    
    f = open(model_name+"/"+fault_name+"_sem2d.hdr")
    lines = f.readlines()
    data['nx'] = int(lines[1].split()[0])
    ndat       = int(lines[1].split()[1])
    data['nt'] = int(lines[1].split()[2])
    data['dt'] = float(lines[1].split()[3])
    xyz = []
    for line in lines[4::]:
        xyz.append(line.split())
    xyz = np.asarray(xyz).astype(np.float64)
    data['x'] = xyz[:,0]
    data['z'] = xyz[:,1]

    # Read initial fault data
    f = open(model_name+"/"+fault_name+"_init_sem2d.tab")
    lines = f.readlines()
    xyz = []
    for line in lines[4::]:
        xyz.append(line.split())
    xyz = np.asarray(xyz).astype(np.float64)
    data['st0'] = xyz[:,0]
    data['sn0'] = xyz[:,1]
    data['mu0'] = xyz[:,2]
    
    # Read fault data in a big matrix
    f   = open(model_name+"/"+fault_name+"_sem2d.dat", "rb")
    dt  = np.dtype((np.float32, data['nx']+2*LENTAG))
    raw = np.fromfile(f, dtype=dt)

    raw = np.reshape(raw[:,LENTAG:LENTAG+data['nx']],(int(raw.shape[0]/ndat),ndat, data['nx']));

    # Reformat each field [nx,nt]
    data['d']  = raw[:,0,:] 
    data['v']  = raw[:,1,:] 
    data['st'] = raw[:,2,:] 
    data['sn'] = raw[:,3,:] 
    data['mu'] = raw[:,4,:] 
    if (ndat == 5+4):
        data['d1t'] = raw[:,5,:] 
        data['d2t'] = raw[:,6,:] 
        data['v1t'] = raw[:,7,:] 
        data['v2t'] = raw[:,8,:] 
    elif (ndat == 5+4*2):
        data['d1t'] = raw[:,5,:] 
        data['d1n'] = raw[:,6,:] 
        data['d2t'] = raw[:,7,:] 
        data['d2n'] = raw[:,8,:] 
        data['v1t'] = raw[:,9,:] 
        data['v1n'] = raw[:,10,:] 
        data['v2t'] = raw[:,11,:] 
        data['v2n'] = raw[:,12,:] 

    return data

###



def cumulative_simpson(y, x):
    """
    Version vectorisée de l'intégrale cumulative de Simpson.
    Supporte y de forme (n,) ou (n_signaux, n)
    x doit être 1D de taille n.
    """
    y = np.asarray(y)
    x = np.asarray(x)

    if y.ndim == 1:
        y = y[np.newaxis, :]  # Devient (1, n)

    n_signaux, n = y.shape
    if x.shape[0] != n:
        raise ValueError("x doit avoir la même taille que l'axe temps de y")

    cumint = np.zeros((n_signaux, n))
    idx = np.arange(2, n, 2)
    h = x[idx] - x[idx - 2]  # h shape = (k,)

    y0 = y[:, idx - 2]
    y1 = y[:, idx - 1]
    y2 = y[:, idx]

    area = (h / 6) * (y0 + 4 * y1 + y2)  # broadcast : (n_signaux, k)

    cum = np.cumsum(area, axis=1)
    cumint[:, idx] = cum

    # Interpolation linéaire sur les indices impairs
    for i in range(1, n, 2):
        if i + 1 < n:
            cumint[:, i] = 0.5 * (cumint[:, i - 1] + cumint[:, i + 1])
        else:
            cumint[:, i] = cumint[:, i - 1]

    # Si entrée 1D, retourne aussi 1D
    if cumint.shape[0] == 1:
        return cumint[0]
    return cumint



# def compute_displacement(V,T):
#     U = cumulative_simpson(V,x=T)
#     return np.insert(U,0,0)
# ###

def compute_displacement(V,T):
    U = cumulative_simpson(V,x=T)
    return U
###

def compute_acceleration(V,T):
    dt = T[1] - T[0]
    if V.ndim != 1:
        A = np.gradient(V, dt, axis=1)
    else:
        A = np.gradient(V, dt)
    return A
###

def draw_example(ax, lw=0.5):
    ax.plot([-10, -10], [-30, 30], 'k', lw=lw)
    ax.plot([10, 10], [-30, 30], 'k', lw=lw)
    ax.plot([-10, 10], [-30, -30], 'k', lw=lw)
    ax.plot([-10, 10], [30, 30], 'k', lw=lw)
    ax.plot([-250, 250], [0, 0], 'k', lw=lw/1.5)
    ax.set_xlim(-100, 100)
    ax.set_ylim(-60, 35)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")
###

def get_nearest_station(x,z, XSTA, ZSTA):
    dist = np.sqrt((XSTA-x)**2+(ZSTA-z)**2)
    s_index = np.argmin(dist)
    return s_index
###

def plot_seismogram(ax, station, comp, val, dic):
    T, U, V, c = dic[comp]
    U, V = U[:,station], V[:,station]
    if val=='U':
        ax.plot(T, U, color=c)
        ax.set_ylabel("Displacement (m)")
    elif val=='V':
        ax.plot(T, V, color=c)
        ax.set_ylabel("Velocity (m/s)")
    else :
        raise Exception('Not a valid component')
    ax.set_xlabel("Time (s)")
###

def zero_pad(signal, N):
    return np.pad(signal, (0,N*signal.size), 'constant')
###

def plot_input_signal(time, input_velocity, config, fig=None, fmin=0.01, fmax=50, Amax=1e3):
    """
    Configurations :
    - VU : Velocity (V) / Displacement (U) plot
    - VF : Velocity (V) / Velocity Spectrum (F) plot
    """

    #Create figure if not given
    if fig ==  None:
        fig = plt.figure()
    
    fig.suptitle("Input signal")
    fig.subplots_adjust(wspace=0.5)

    #Create axes
    ax_V, ax_2 = fig.subplots(1,2)
    ax_2.set_aspect('auto')

    #Create velocity plot
    ax_V.set_xlabel("Time (s)")
    ax_V.set_ylabel("Velocity (m/s)")
    ax_V.set_title("Input velocity")
    ax_V.grid(True)
    ax_V.plot(time, input_velocity, c='b', label='Input Velocity SEM2DPACK')
    
    if config=='VU':
        #Create displacement plot
        input_displacement = compute_displacement(input_velocity, time)
        ax_2.set_xlabel("Time (s)")
        ax_2.set_ylabel("Displacement (m)")
        ax_2.set_title("Input displacement")
        ax_2.grid(True)
        ax_2.plot(time, input_displacement, c='b', label='Input Displacement SEM2DPACK')
    
    elif config=='VF':
        #Create Fourier plot
        # FFT, freq = fourier(zero_pad(input_velocity, N=2),time[1]-time[0])
        FFT, freq = fourier(input_velocity,time[1]-time[0])
        ax_2.set_xlabel("Frequency (Hz)")
        ax_2.set_ylabel("Spectral amplitude (m)")
        ax_2.set_title("Fourier transform")
        ax_2.grid(True)
        ax_2.set_xscale('log')
        ax_2.set_yscale('log')
        ax_2.set_xlim(fmin, fmax)
        ax_2.set_ylim(1e-5, Amax)
        ax_2.plot(freq, FFT, c='b', label='Velocity Fourier Transform SEM2DPACK')

    return fig, ax_V, ax_2
###

def get_stations_from_layers(layers, xlim, zmin, XSTA, ZSTA):
    stations = []
    level = [0]
    for i in range(1,len(layers)):
        level.append(level[-1]-layers[i-1])
    Z_pos = (level + np.append(level[1:],zmin))/2
    x = (xlim[0]+xlim[1])/2
    for z in Z_pos:
        stations.append(get_nearest_station(x, z, XSTA, ZSTA))
    return np.array(stations)
###

def write_FLAC_input_signal_table(input_signal_SEM_path):
    """
    Write the input signal table for FLAC3D input
    """
    #Load input signal
    input_signal = np.genfromtxt(open(input_signal_SEM_path,'r'))
    time_input = input_signal[:,0]
    V_input = input_signal[:,1]
    #Write the input signal table
    file = open("./Input_Signal_Table.txt", 'w+')
    file.write("Input signal\n")
    file.write(str(time_input.size) + "  " + str(time_input[1]-time_input[0]) + "\n")
    for i in V_input:
        file.write(str(i) + "\n")
    file.close()
###

def stockwell(data,tempo, delta=None):
    from stockwell import st
    import scipy as sp

    """
    Credit: https://github.com/fiorellalan/Seismic-Intensity-Measure/tree/main
    :param data : array of amplitude, type=np.array
    :parm tipe : array of time samples, type=np.array
    """

    fny = 1/(2*delta)
    df = 1/(tempo[-1]-tempo[0])
    nfreq =int(fny/df)
    
    print ("Nyquist", fny)
    while fny > 50:
        data,tempo=sp.signal.resample(data,int(len(data)/2),t=tempo)
        delta =  tempo[1]-tempo[0]
        fny = (1./(2*delta))
        nfreq =int(fny/df)
        df = 1/(tempo[-1]-tempo[0])
        print ("Nyquist", fny)

    fmin = df
    low =int(fmin/df) 
    print ("low", fmin/df,low)
        
    stock = st.st(data,low,nfreq)
    stock = np.flipud(stock)

    time = []
    for i_time in range(len(data)):
        time.append(i_time*delta)

    freq=[]
    for i_freq in range(1,nfreq+1):
        freq.append(i_freq*df)

    X,Y = np.meshgrid(time,freq)
    
    halfbin_time = delta/2.
    halfbin_freq = df/2.
    

    extent = (time[0] , time[-1], freq[0], freq[-1])
    return stock,X,Y,extent
###

def plot_spectrogram(t, signal, fig=None, mappable=None, yscale='linear'):

    #Compute the Stockwell Transform of the signal
    stock, _, _, extent = stockwell(signal,t, delta=t[1]-t[0])

    #Create a figure if not given
    if fig == None:
        fig = plt.figure()

    fig.suptitle("Spectrogram")

    #Create the axes
    ax, cax = fig.subplots(1,2,width_ratios=(1,0.05))
    

    #Load ScalarMappable data
    if mappable != None:
        cmap = mappable.get_cmap()
        clim = mappable.get_clim()
    else:
        cmap = 'plasma'
        clim = [None, None]

    #Plot the spectrogram
    im = ax.imshow(np.abs(stock), interpolation='spline16', extent=extent, cmap=cmap, vmin=clim[0], vmax=clim[1])
    ax.set_xlim(extent[0], extent[1])
    ax.set_xlabel("Time (s)")
    ax.set_ylim(0.1, extent[3])
    ax.set_ylabel("Frequency (Hz)")
    ax.set_yscale(yscale)
    ax.axis('tight')

    #Add a colorbar
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label("Stockwell Magnitude")

    return fig

###

def read_grid(filepath):
    values = pd.read_csv(filepath, header=None).to_numpy()
    print(values.shape)
    grid = np.array([])
    for i, line in enumerate(values):
        val = np.array(line[0].split(),dtype=float)
        if i%2==0:
            line_values = np.array([])
            line_values = np.concatenate([line_values, val], axis=0)
        else:
            line_values = np.concatenate([line_values, val], axis=0)
            if i==1:
                grid = np.concatenate([grid,line_values], axis=0)
            else:
                grid = np.vstack([grid,line_values])
    return grid
###

def read_grid_values(filepath):
    values = pd.read_csv(filepath, header=None).to_numpy()
    stock = np.array([])
    for i in range(values.size):
        if i==0:
            stock = np.array(values[i][0].split(), dtype=float)
        else:
            stock = np.vstack([stock, np.array(values[i][0].split(), dtype=float)])
    return stock
###

def import_SEM_grid(dir):
    grid = read_grid(dir+'USER_2D_grid.inp')
    e, ii, jj, X, Z = grid[:,0].astype(int), grid[:,1].astype(int), grid[:,2].astype(int), grid[:,3], grid[:,4]
    grid_values = read_grid_values(dir+'USER_2D_grid_values.inp')
    Vs, Vp = grid_values[:,3], grid_values[:,4]
    SEM_grid = {"e" : e, "ii" : ii, "jj" : jj, "X_grid" : X, "Z_grid" : Z, "Vs" : Vs, "Vp" : Vp}
    return SEM_grid

###

def visualize_grid(grid, component='Vs', ax=None):
    X = grid['X_grid']
    Z = grid['Z_grid']
    Vs = grid[component]

    soil_mask = (Z <= 0)
    structure_mask = (np.abs(Z) < 30) & (np.abs(X) < 10)
    norm = colors.Normalize(np.min(Vs), np.max(Vs))
    cmap = 'terrain'
    SM = cm.ScalarMappable(norm=norm, cmap=cmap)
    if ax is None:
        fig, ax = plt.subplots()
    ax.tricontourf(X[soil_mask], Z[soil_mask], Vs[soil_mask], levels=50, cmap=cmap, norm=norm)
    ax.tricontourf(X[structure_mask], Z[structure_mask], Vs[structure_mask], levels=50, cmap=cmap, norm=norm)
    draw_example(ax)
    ax.set_xlim([-250,250])
    ax.set_ylim([-100,30])
    plt.colorbar(SM, ax=ax)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")
    ax.set_title(f"{component} distribution in the soil")

###

def compute_soil_mean(grid, window, component='Vs'):
    """
    Compute the mean value of a given component in the soil
    """
    X = grid['X_grid']
    Z = grid['Z_grid']
    val = grid[component]

    structure_mask = (np.abs(Z) < 30) & (np.abs(X) < 10)
    mean_mask = (-30-window < Z) & (Z < 0) & (np.abs(X) < 10+window)
    total_mask = ~structure_mask & mean_mask
    mean_value = np.mean(val[total_mask])
    
    print(f"Mean {component} in the soil: {mean_value:.2f}")
    return mean_value
###
def compute_spatial_frequencies(Lx, Lz, Nx, Nz):
    """ 
    Function which compute the spatial frequencies of a grid

    Parameters :
    Lx, Lz : Domain lengths
    Nx, Nz : Number of points in the domain
    """
    kx = 2*np.pi*np.fft.fftfreq(Nx, Lx/Nx)
    kz = 2*np.pi*np.fft.fftfreq(Nz, Lz/Nz)
    return kx, kz