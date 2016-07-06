# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 13:19:35 2016

@author: HATLAB
"""

import h5py

import matplotlib.pyplot as plt
import matplotlib.colors as color
import numpy as np

h5py_filepath = 'C:\\Qtlab\\flux_sweep_data\\'
h5py_filename = 'signal_sweep_7_6_2016_11_54'

fp2 = h5py.File(h5py_filepath + h5py_filename, 'r') 

current_data = fp2['current_data']
total_sweeps = len(current_data)
for i in range(total_sweeps):
    freq=fp2['f_data'+str(i)] 
ar_freq = freq[:]
ar_current_data = [float(i) for i in current_data[:]]

array = np.zeros([total_sweeps,len(freq)])

for i in range(total_sweeps):
    trace = fp2['trace_data'+str(i)][:]
    array[i]=trace[0]

fp2.close()

# color map setting
levels=[180, 90, 0, -90, -180]
colors=[color.hex2color('#000000'), color.hex2color('#FF0000'), 
        color.hex2color('#FFFF00'), color.hex2color('#00FF00'),
        color.hex2color('#000000')]
levels=levels[::-1]
colors=colors[::-1]
_cmap=color.LinearSegmentedColormap.from_list('my_cmap', colors)
_norm=color.Normalize(vmin=-180, vmax=180)


if ar_current_data[0] > ar_current_data[-1]:
    array = array[::-1]
plt.imshow(array.transpose(), interpolation='nearest', aspect='auto', origin = 'lower', cmap=_cmap, norm=_norm)

y=np.linspace(ar_freq[0], ar_freq[-1], 21)/1e9
y_space=[float(1601)/20*float(val) for val in range(len(y))]

plt.title('Plot from %s' % h5py_filename)
plt.yticks(np.array(y_space), y)
plt.ylabel('frequency(GHz)')


num_x_ticks = 20
x_ticks = np.arange(ar_current_data[0], ar_current_data[-1], (ar_current_data[-1] - ar_current_data[0])/num_x_ticks)
x_loc=[len(ar_current_data)/float(num_x_ticks)*i for i in range(num_x_ticks)]
plt.xticks(x_loc, x_ticks*1000, rotation=90)
plt.xlabel('Current (mA)')
plt.colorbar().set_label('phase(degrees)')
plt.show()
