# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:30:18 2016

@author: HATLAB : Erick Brindock
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import h5py
import numpy as np
import gainsweep as sweep

class GainSweepPlot(object):
    def __init__(self, filename = None, frequencies = None, powers = None,
                 gains = None, measurement_frequencies = None):
        '''
        Initializes a GainSweepPlot object.  The data to be plotted can be 
        initialized from a properly formatted h5py file or passed in manually 
        using the keyword arguemnts.
        
        h5py should have the following datasets:
            pump_frequencies : the pump frequencies swept through
            pump_powers : the pump powers swept through
            measure_frequencies : the frequency values for the measured gains
            normal_data : the gains used to normalize raw data
            sweep_data : a 3d array of gain values to be plotted against 
                measure frequencies where [frequency][power][data] represent 
                the order of indices
        
            Args:
                filename (string) : the path and filename to read data from
                frequencies (numpy.ndarray) : the frequencies the pump was 
                    swept through
                powers (numpy.ndarray) : the powers the pump was swept through
                gains (numpy.ndarray) : the measured gains
                measurement_frequencies (numpy.ndarray) : the frequencies the 
                    measurement was taken over
        '''
        if filename is not None:
            self.load_data_from_file(filename)
        else:
            self.add_data_set(frequencies, powers, gains, measurement_frequencies)
    def plot_data_from_sweep(self, sweep):
        self.add_data_set(frequencies = sweep.FREQUENCIES, powers = sweep.POWERS,
                          gains = sweep.SWEEP_DATA-sweep.NORMALIZE_DATA[0],
                          measurement_frequencies = sweep.MEASURED_FREQUENCIES)
        self.plot_data()
    def plot_data(self):
        '''
        Sets up the plot window, adds sliders to the plot and displays it
        '''
        # Main Data Plot Setup
        self.data_plot, = plt.plot(self.measurement_frequency, self.gain[0,0])
        plt.axis([self.measurement_frequency[0], self.measurement_frequency[-1], -5, 35])
        plt.gcf().subplots_adjust(left = .05, right = .95,top = .95, bottom = .15)
        plt.title('Power and Frequency Sweep')
        plt.xlabel('Frequency (Ghz)')
        plt.ylabel('Gain (dB)')
        # Slider Setup
        self.freq_axes = plt.axes([0.2, 0.01, 0.65, 0.03])
        self.freq_slider = Slider(self.freq_axes, 'Frequency', 
                                  min(self.sweep_freqs), max(self.sweep_freqs),
                             valinit=min(self.sweep_freqs), valfmt = '%.0f Hz')
        self.power_axes = plt.axes([0.2, 0.05, 0.65, 0.03])
        self.power_slider = Slider(self.power_axes, 'Power', min(self.sweep_powers),
                                   max(self.sweep_powers), 
                            valinit=min(self.sweep_powers), valfmt = '%.1f dBm')
        self.power_slider.on_changed(self.update)
        self.freq_slider.on_changed(self.update)
        plt.show()
            
    def update(self, val):
        '''
        Updates the data plotted when the sliders are changed
            Input:
                val : the value passed in from the slider
        '''
        sval = int(self.power_slider.val*10)/10.0
        fval = self.freq_slider.val
        findex = self.sweep_freqs.index(min(self.sweep_freqs, key=lambda x:abs(x-fval)))
        pindex = self.sweep_powers.index(min(self.sweep_powers, key=lambda x:abs(x-sval)))    
        self.data_plot.set_ydata(self.gain[findex][pindex])
        if (self.power_slider.val != self.sweep_powers[pindex]):
            self.power_slider.set_val(self.sweep_powers[pindex])
        if (self.freq_slider.val != self.sweep_freqs[findex]):
            self.freq_slider.set_val(self.sweep_freqs[findex])
            
    def add_data_set(self, frequencies, powers, gains, measurement_frequencies):
        self.sweep_freqs = frequencies
        self.sweep_powers = powers
        self.gain = gains
        self.measurement_frequency = measurement_frequencies
        
    def load_data_from_file(self, 
            filename='C:\\Qtlab\\gain_sweep_data\\JPC_pump_sweep_7_6_2016_15'):
        '''
        Loads data from a file to be plotted
            Args:
                filename (string) : the filepath and file name to be plotted
        '''
        infile = h5py.File(filename, 'a')
        self.sweep_freqs = infile['pump_frequencies'][:]
        self.sweep_freqs = self.sweep_freqs.tolist()
        self.sweep_powers = infile['pump_powers'][:]
        self.sweep_powers = self.sweep_powers.tolist()
        for i in range(len(self.sweep_powers)):  # Remove floating point error
            self.sweep_powers[i] = int(self.sweep_powers[i]*10)/10.0
        self.gain = np.array(infile['sweep_data'])
        self.measurement_frequency = infile['measure_frequencies'][:]
        #TODO changed to normal_data check fro proper format of file used
        self.normalize_data = infile['normal_data'][0]
        self.gain = np.subtract(self.gain, self.normalize_data)
        infile.close()