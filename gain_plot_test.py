# -*- coding: utf-8 -*-
"""
Created on Wed Jul 06 15:33:03 2016

@author: HATLAB
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import h5py
import numpy as np

# Load Data from h5py File
fp = h5py.File('C:\\Qtlab\\gain_sweep_data\\JPC_pump_sweep_7_6_2016_15', 'r')

sweep_freqs = fp['frequencies'][:]
sweep_freqs = sweep_freqs.tolist()
sweep_powers = fp['powers'][:]
sweep_powers = sweep_powers.tolist()
for i in range(len(sweep_powers)):  # Remove floating point error
    sweep_powers[i] = int(sweep_powers[i]*10)/10.0
gain = []
for fi in range(len(sweep_freqs)):
    for pi in range(len(sweep_powers)):
        gain.append(fp['trace_data_{}_{}'.format(sweep_powers[pi], sweep_freqs[fi])][0])
measurement_frequency = fp['fdata_{}_{}'.format(sweep_powers[0], sweep_freqs[0])][:]

fp.close()

# Main Data Plot Setup
data_plot, = plt.plot(measurement_frequency, gain[10])
plt.axis([measurement_frequency[0], measurement_frequency[-1], -5, 30])
plt.gcf().subplots_adjust(left = .05, right = .95,top = .95, bottom = .15)
plt.title('Power and Frequency Sweep')
plt.xlabel('Frequency (Ghz)')
plt.ylabel('Gain (dBm)')

# Slider Setup
freq_axes = plt.axes([0.2, 0.01, 0.65, 0.03])
freq_slider = Slider(freq_axes, 'Frequency', min(sweep_freqs), max(sweep_freqs), valinit=min(sweep_freqs), valfmt = '%.0f Hz')
power_axes = plt.axes([0.2, 0.05, 0.65, 0.03])
power_slider = Slider(power_axes, 'Power', min(sweep_powers), max(sweep_powers), valinit=min(sweep_powers), valfmt = '%.1f dB')

def update(val):
    sval = int(power_slider.val*10)/10.0
    fval = freq_slider.val
    findex = sweep_freqs.index(min(sweep_freqs, key=lambda x:abs(x-fval)))
    pindex = sweep_powers.index(min(sweep_powers, key=lambda x:abs(x-sval)))
    index = pindex + (findex*len(sweep_powers))    
    data_plot.set_ydata(gain[index])
    if (power_slider.val != sweep_powers[pindex]):
        power_slider.set_val(sweep_powers[pindex])
    if (freq_slider.val != sweep_freqs[findex]):
        freq_slider.set_val(sweep_freqs[findex])
        
power_slider.on_changed(update)
freq_slider.on_changed(update)
plt.show()
