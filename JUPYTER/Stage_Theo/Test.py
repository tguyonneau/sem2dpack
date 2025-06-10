import sys
import os
sys.path.append('./JUPYTER/modules/')

from Stage_module import *



import matplotlib.pyplot as plt
import numpy as np

t = np.arange(0, 20, 1e-1)
dt = t[1] - t[0]
f= 0.5

y1 = 4*np.exp(-(t-5)**2/(2*2**2))*np.sin(2*np.pi*f*t)
y2 = 2*np.exp(-(t-10)**2/(2*4**2))*np.sin(2*2*np.pi*f*t)
y3 = 3*np.exp(-(t-15)**2/(2*2**2))*np.sin(4*2*np.pi*f*t)
y = y1 + y2 + y3

# input_signal = np.genfromtxt(open('./JUPYTER/Stage_Theo/SourcesTime_sem2d.tab','r'))
# t = input_signal[:,0]
# y = input_signal[:,1]
# dt = t[1] - t[0]

stock, X, Y, extent = stockwell(y,t, delta=dt)

figA = plt.figure(constrained_layout=True)
subfigs = figA.subfigures(2,1)
fig1 = subfigs[0]
fig2 = subfigs[1]

plot_input_signal(t, y, 'VF', fig=fig1)
plot_spectrogram(t, y, yscale='log', fig=fig2)


figB = plt.figure()
ax = figB.add_subplot(1,1,1, projection='3d')
ax.plot_surface(X, Y, np.abs(stock), cmap='plasma')
ax.set_xlabel("Time(s)")
ax.set_ylabel("Frequency (Hz)")
ax.set_zlabel("Stockwell Magnitude")

plt.show()