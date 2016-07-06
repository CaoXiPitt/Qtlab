# -*- coding: utf-8 -*-
"""
Created on Wed Jul 06 15:33:03 2016

@author: HATLAB
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import h5py
import numpy as np

fp = h5py.File('C:\\Qtlab\\gain_sweep_data\\JPC_pump_sweep_7_6_2016_15', 'r')
#print fp['trace_data_]
test_data = np.array([[1,2,3], [1,2,3]])
#plt.plot(test_data[0], test_data[1])


freqs = fp['frequencies'][:]
pows = fp['powers'][:]
freq_index =int(len(freqs)/2)
#TODO get array of gains from fp file
gain = fp['trace_data_{}_{}'.format(pows[0], freqs[freq_index])][0]
mfrequency = fp['fdata_{}_{}'.format(pows[0], freqs[freq_index])]



data_plot, = plt.plot(mfrequency, gain)
plt.axis([mfrequency[0], mfrequency[-1], -5, 30])
ax_power = plt.axes([0.2,0.01, 0.65, 0.03])
sl_power = Slider(ax_power, 'Power', 0, 20, valinit=0)
print pows.tolist()
def update(val):
    #TODO figure out method to update slider
    val = int(val)
    index = int(val)
    print index
    data_plot.set_ydata(gain[index])
    if (sl_power.val != pows[index]):
        sl_power.set_val(pows[index])
        
sl_power.on_changed(update)
plt.show()
#for i in range(22):
#    freq_index =int(len(freqs)/2)]
#    gain = fp['trace_data_{}_{}'.format(pows[i], freqs[freq_index])][0]
#    mfrequency = fp['fdata_{}_{}'.format(pows[i], freqs[freq_index])]
#    plt.plot(mfrequency, gain)
#    plt.xlabel('frequency(Hz)')
#    plt.ylabel('gain(dB)')
#    plt.ylim((-5, 30))
#    plt.title('Plot at {} {}'.format(pows[i],freqs[freq_index]))
#    plt.show()
fp.close()