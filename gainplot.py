# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:30:18 2016

@author: HATLAB : Erick Brindock
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import h5py
import numpy as np

class GainSweepPlot(object):
    def __init__(self, filename = None, frequencies = None, powers = None,
                 gains = None):
        if filename is not None:
            self.load_data_from_file(filename)
        else:
            self.sweep_freqs = frequencies
            self.sweep_powers = powers
            self.gains = gains
            
    # Load Data from h5py File
#    fp = h5py.File('C:\\Qtlab\\gain_sweep_data\\JPC_pump_sweep_7_6_2016_15', 'r')
#    
#    sweep_freqs = fp['frequencies'][:]
#    sweep_freqs = sweep_freqs.tolist()
#    sweep_powers = fp['powers'][:]
#    sweep_powers = sweep_powers.tolist()
#    for i in range(len(sweep_powers)):  # Remove floating point error
#        sweep_powers[i] = int(sweep_powers[i]*10)/10.0
#    gain = []
#    for fi in range(len(sweep_freqs)):
#        for pi in range(len(sweep_powers)):
#            gain.append(fp['trace_data_{}_{}'.format(sweep_powers[pi], sweep_freqs[fi])][0])
#    measurement_frequency = fp['fdata_{}_{}'.format(sweep_powers[0], sweep_freqs[0])][:]
#    
#    fp.close()
    def plot_data(self):
        # Main Data Plot Setup
        self.data_plot, = plt.plot(self.measurement_frequency, self.gain[10])
        plt.axis([self.measurement_frequency[0], self.measurement_frequency[-1], -5, 30])
        plt.gcf().subplots_adjust(left = .05, right = .95,top = .95, bottom = .15)
        plt.title('Power and Frequency Sweep')
        plt.xlabel('Frequency (Ghz)')
        plt.ylabel('Gain (dBm)')
        # Slider Setup
        self.freq_axes = plt.axes([0.2, 0.01, 0.65, 0.03])
        self.freq_slider = Slider(self.freq_axes, 'Frequency', 
                                  min(self.sweep_freqs), max(self.sweep_freqs),
                             valinit=min(self.sweep_freqs), valfmt = '%.0f Hz')
        self.power_axes = plt.axes([0.2, 0.05, 0.65, 0.03])
        self.power_slider = Slider(self.power_axes, 'Power', min(self.sweep_powers),
                                   max(self.sweep_powers), 
                            valinit=min(self.sweep_powers), valfmt = '%.1f dB')
        self.power_slider.on_changed(self.update)
        self.freq_slider.on_changed(self.update)
        plt.show()
        
#    def update(self, val):
#        sval = int(self.power_slider.val*10)/10.0
#        fval = self.freq_slider.val
#        findex = self.sweep_freqs.index(min(self.sweep_freqs, key=lambda x:abs(x-fval)))
#        pindex = self.sweep_powers.index(min(self.sweep_powers, key=lambda x:abs(x-sval)))
#        index = pindex + (findex*len(self.sweep_powers))    
#        self.data_plot.set_ydata(self.gain[index])
#        if (self.power_slider.val != self.sweep_powers[pindex]):
#            self.power_slider.set_val(self.sweep_powers[pindex])
#        if (self.freq_slider.val != self.sweep_freqs[findex]):
#            self.freq_slider.set_val(self.sweep_freqs[findex])
            
#    power_slider.on_changed(update)
#    freq_slider.on_changed(update)
#    plt.show()
#    def load_data_from_file(self, 
#            filename='C:\\Qtlab\\gain_sweep_data\\JPC_pump_sweep_7_6_2016_15'):
#        infile = h5py.File(filename, 'a')
#        self.sweep_freqs = infile['frequencies'][:]
#        self.sweep_freqs = self.sweep_freqs.tolist()
#        self.sweep_powers = infile['powers'][:]
#        self.sweep_powers = self.sweep_powers.tolist()
#        for i in range(len(self.sweep_powers)):  # Remove floating point error
#            self.sweep_powers[i] = int(self.sweep_powers[i]*10)/10.0
#        self.gain = []
#        for fi in range(len(self.sweep_freqs)):
#            for pi in range(len(self.sweep_powers)):
#                self.gain.append(infile['trace_data_{}_{}'.format(self.sweep_powers[pi], self.sweep_freqs[fi])][0])
#        self.measurement_frequency = infile['fdata_{}_{}'.format(self.sweep_powers[0], self.sweep_freqs[0])][:]
#        infile.close()
            
    def update(self, val):
        sval = int(self.power_slider.val*10)/10.0
        fval = self.freq_slider.val
        findex = self.sweep_freqs.index(min(self.sweep_freqs, key=lambda x:abs(x-fval)))
        pindex = self.sweep_powers.index(min(self.sweep_powers, key=lambda x:abs(x-sval)))
        #index = pindex + (findex*len(self.sweep_powers))    
        self.data_plot.set_ydata(self.gain[findex][pindex])
        if (self.power_slider.val != self.sweep_powers[pindex]):
            self.power_slider.set_val(self.sweep_powers[pindex])
        if (self.freq_slider.val != self.sweep_freqs[findex]):
            self.freq_slider.set_val(self.sweep_freqs[findex])
            
    def load_data_from_file(self, 
            filename='C:\\Qtlab\\gain_sweep_data\\JPC_pump_sweep_7_6_2016_15'):
        infile = h5py.File(filename, 'a')
        self.sweep_freqs = infile['frequencies'][:]
        self.sweep_freqs = self.sweep_freqs.tolist()
        self.sweep_powers = infile['powers'][:]
        self.sweep_powers = self.sweep_powers.tolist()
        for i in range(len(self.sweep_powers)):  # Remove floating point error
            self.sweep_powers[i] = int(self.sweep_powers[i]*10)/10.0
        self.gain = np.array(infile['sweep_data'])
#        for fi in range(len(self.sweep_freqs)):
#            for pi in range(len(self.sweep_powers)):
#                self.gain.append(infile['trace_data_{}_{}'.format(self.sweep_powers[pi], self.sweep_freqs[fi])][0])
        self.measurement_frequency = infile['fdata_{}_{}'.format(self.sweep_powers[0], self.sweep_freqs[0])][:]
        infile.close()