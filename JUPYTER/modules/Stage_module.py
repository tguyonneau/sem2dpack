import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from houches_fb import *
from scipy.integrate import cumulative_simpson




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

        # Data file III
        # Read potency and potency rate, currently only for out-of-plane (ndof=1)
        # for in-plane models change usecols and potency* arrays' size
        fname = self.directory+'/Flt'+str('%02d' % BC[0])+'_potency_sem2d.tab'        
        if os.path.exists(fname):
            print(fname)
            # POTENCY
            # out-of plane model -- compo 13
            # replace D by e for python 
            array = np.genfromtxt(fname,usecols=0, dtype=None,  encoding=None)
            array_fixed  = np.array( [float(dum.replace('D','e')) for dum in array])
            fault['potency'] = np.zeros((array_fixed.shape[0], 2))
            fault['potency_rate'] = np.zeros((array_fixed.shape[0], 2))    
            fault['potency'][:,0] = array_fixed
            
            # out-of plane model -- compo 23
            array = np.genfromtxt(fname,usecols=1, dtype=None,  encoding=None)
            array_fixed  = np.array( [float(dum.replace('D','e')) for dum in array])    
            fault['potency'][:,1] = array_fixed
            
            # POTENCY RATE
            # out-of plane model -- compo 13
            array = np.genfromtxt(fname,usecols=2, dtype=None,  encoding=None)
            array_fixed  = np.array( [float(dum.replace('D','e')) for dum in array])    
            fault['potency_rate'][:,0] = array_fixed
                
            # out-of plane model -- compo 23
            array = np.genfromtxt(fname,usecols=3, dtype=None,  encoding=None)
            array_fixed  = np.array( [float(dum.replace('D','e')) for dum in array])    
            fault['potency_rate'][:,1] = array_fixed    

    self.fault = fault        

    # Find the earthquake
    if is_rate_and_state:
        cdt_beg = (self.fault['isDyn']==True) & (np.roll(self.fault['isDyn'], 1)==False)
        cdt_end = (self.fault['isDyn']==True) & (np.roll(self.fault['isDyn'], -1)==False)
        index = np.arange(0, len(self.fault['isDyn']))
        print ('Number of dynamic beginning and ending points:', len(index[cdt_beg]), len(index[cdt_end]))   
    ##
    return

def compute_displacement(V,T):
    U = cumulative_simpson(V,x=T)
    return np.insert(U,0,0)

def draw_example(ax, lw=0.5):
    ax.plot([-10, -10], [-30, 30], 'k', lw=lw)
    ax.plot([10, 10], [-30, 30], 'k', lw=lw)
    ax.plot([-10, 10], [-30, -30], 'k', lw=lw)
    ax.plot([-10, 10], [30, 30], 'k', lw=lw)
    ax.plot([-100, 100], [0, 0], 'k', lw=lw/1.5)
    ax.set_xlim(-100, 100)
    ax.set_ylim(-60, 35)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")

def get_nearest_station(x,z, XSTA, ZSTA):
    dist = np.sqrt((XSTA-x)**2+(ZSTA-z)**2)
    s_index = np.argmin(dist)
    return s_index

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

def zero_pad(signal, N):
    return np.pad(signal, (0,N*signal.size), 'constant')

def plot_input_signal(input_signal_path, config, fmin=0.01, fmax=50, pad=2, Amax=1e1):
    """
    Configurations :
    - VU : Velocity (V) / Displacement (U) plot
    - VF : Velocity (V) / Velocity Spectrum (F) plot
    """
    #Load input signal
    input_signal = np.genfromtxt(open(input_signal_path,'r'))
    time = input_signal[:,0]
    input_velocity = input_signal[:,1]

    #Create figure
    fig = plt.figure()
    fig.subplots_adjust(wspace=0.5)
    fig.suptitle("Input signal")

    #Create velocity plot
    ax_V = fig.add_subplot(1,2,1, aspect='auto')
    ax_V.set_xlabel("Time (s)")
    ax_V.set_ylabel("Velocity (m/s)")
    ax_V.set_title("Input velocity")
    ax_V.grid(True)
    ax_V.plot(time, input_velocity)
    
    if config=='VU':
        #Create displacement plot
        input_displacement = compute_displacement(input_velocity, time)
        ax_D = fig.add_subplot(1,2,2, aspect='auto')
        ax_D.set_xlabel("Time (s)")
        ax_D.set_ylabel("Displacement (m)")
        ax_D.set_title("Input displacement")
        ax_D.grid(True)
        ax_D.plot(time, input_displacement)
    
    elif config=='VF':
        #Create Fourier plot
        FFT, freq = fourier(zero_pad(input_velocity, N=2),time[1]-time[0])
        ax_F = fig.add_subplot(1,2,2, aspect='auto')
        ax_F.set_xlabel("Frequency (Hz)")
        ax_F.set_ylabel("Spectral amplitude (m)")
        ax_F.set_title("Fourier transform")
        ax_F.grid(True)
        ax_F.set_xscale('log')
        ax_F.set_yscale('log')
        ax_F.set_xlim(fmin, fmax)
        ax_F.set_ylim(1e-5, Amax)
        ax_F.plot(freq, FFT)

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