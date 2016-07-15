# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:30:18 2016

@author: HATLAB : Erick Brindock
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import h5py
import numpy as np
#import gainsweep as sweep

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
        elif (frequencies is not None and powers is not None and gains is not None and measurement_frequencies is not None):
            self.add_data_set(frequencies, powers, gains, measurement_frequencies)
    def plot_data_from_sweep(self, sweep):
        self.gain = np.copy(sweep.SWEEP_DATA)
        self.add_data_set(sweep.CURRENTS,sweep.FREQUENCIES, sweep.POWERS, sweep.SWEEP_DATA,
                          sweep.MEASURE_BANDWIDTH, 
                          background = sweep.NORMALIZE_DATA)
        self.plot_data()
    def plot_data(self):
        '''
        Sets up the plot window, adds sliders to the plot and displays it
        '''
        # Main Data Plot Setup
        self.data_plot, = plt.plot(self.measurement_frequency, self.gain[0,0,0,0])  #added another 0
        plt.axis([self.measurement_frequency[0], self.measurement_frequency[-1], -5, 35])
        plt.gcf().subplots_adjust(left = .05, right = .95,top = .95, bottom = .15)
        plt.title('Power and Frequency Sweep')
        plt.xlabel('Frequency (Ghz)')
        plt.ylabel('Gain (dB)')
        # Slider Setup
        self.freq_axes = plt.axes([0.2, 0.05, 0.65, 0.03])
        self.freq_slider = Slider(self.freq_axes, 'Frequency', 
                                  min(self.sweep_freqs), max(self.sweep_freqs),
                             valinit=min(self.sweep_freqs), valfmt = '%.0f Hz')
        self.power_axes = plt.axes([0.2, 0.09, 0.65, 0.03])
        self.power_slider = Slider(self.power_axes, 'Power', min(self.sweep_powers),
                                   max(self.sweep_powers), 
                            valinit=min(self.sweep_powers), valfmt = '%.1f dBm')
        self.current_axes = plt.axes([0.2, 0.01, 0.65, 0.03])
        self.current_slider = Slider(self.current_axes, 'Power', min(self.currents),
                                   max(self.currents), 
                            valinit=min(self.currents), valfmt = '%.5f A')
        self.current_slider.on_changed(self.update)
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
        cval = self.current_slider.val
        findex = self.sweep_freqs.index(min(self.sweep_freqs, key=lambda x:abs(x-fval)))
        pindex = self.sweep_powers.index(min(self.sweep_powers, key=lambda x:abs(x-sval)))
        cindex = self.currents.index(min(self.currents, key=lambda x:abs(x-cval)))
        self.data_plot.set_ydata(self.gain[cindex][findex][pindex][0])
        if (self.power_slider.val != self.sweep_powers[pindex]):
            self.power_slider.set_val(self.sweep_powers[pindex])
        if (self.freq_slider.val != self.sweep_freqs[findex]):
            self.freq_slider.set_val(self.sweep_freqs[findex])
        if (self.current_slider.val != self.currents[cindex]):
            self.current_slider.set_val(self.currents[cindex])
        
    def add_data_set(self, currents, frequencies, powers, gains, measurement_frequencies, background = None):
        '''
        Adds data to be used to make a plot. If optional background arguemnt is
        included, it will be used to normalize the data contained in the gains 
        arguement.
            Args:
                frequencies (numpy.1darray) : 
                the frequencies swept through
                powers (numpy.1darray) : 
                the powers swept through
                gains (numpy.3darray) : 
                the gains measured for each [frequency, power] (y values)
                measurement_frequencies (numpy.1darray) : 
                the frequencies at which each gain measurement is taken (x val)
                background (numpy.2darray) : 
                the background noise used to normalize the gains
        '''
        self.currents = currents.tolist()
        self.sweep_freqs = frequencies.tolist()
        self.sweep_powers = powers.tolist()
        if background is None:
            self.gain = np.copy(gains)
        else:
            self.normalize_data(background)
        self.measurement_frequency = measurement_frequencies
        
    def normalize_data(self, background):
        '''
        Normalizes the gains using the background. This method assumes that a 
        new background reading is taken for each frequency.
            Args:
                gains (numpy.3darray) : 
                the gains measured for each [frequency, power] (y values)
                background (numpy.2darray) : 
                the background noise used to normalize the gains
                name courtesy of Edan Benjamin Alpern
        '''
        print 'normalizing data'
        #TODO corret normalization for new data structure
        for i in range(self.gain.shape[0]):
            self.gain[i] = self.gain[i]- background[i]
    def load_data_from_file(self, filename, normalized = False):
        '''
        Loads data from an h5py file to be plotted
            Args:
                filename (string) : 
                the filepath and file name to be plotted
            Optional Args:
                normalized (boolean) : 
                whether the gain data has been normalized. If False this method
                will normalize the data using the normalizatoin data in the 
                file
        '''
        infile = h5py.File(filename, 'r')
        self.sweep_freqs = np.array(infile['pump_frequencies'])
        self.sweep_powers = np.array(infile['pump_powers'])
#        for i in range(len(self.sweep_powers)):  # Remove floating point error
#            self.sweep_powers[i] = int(self.sweep_powers[i]*10)/10.0
        self.gain = np.array(infile['sweep_data'])
        self.measurement_frequency = np.array(infile['measure_frequencies'])
        if normalized:
            self.add_data_set(self.sweep_freqs, self.sweep_powers, self.gain,
                                self.measurement_frequency)
        else:
            print type(self)
            self.unpumped_data = np.array(infile['normal_data'])
            self.add_data_set(self.sweep_freqs, self.sweep_powers, self.gain,
                                self.measurement_frequency, 
                                background = self.unpumped_data)
        infile.close()