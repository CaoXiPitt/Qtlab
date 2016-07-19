# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 09:21:07 2016

@author: HATLAB : Erick Brindock
"""
import h5py

import matplotlib.pyplot as plt
import matplotlib.colors as color
from matplotlib.widgets import Cursor
from matplotlib.widgets import Slider
import numpy as np

class GainSweepColorPlot(object):
    def __init__(self, filename = None):
        if filename is not None:
            self.load_data_from_file(filename)
        else:
            print 'Class instantiated with no data'
        
        
    def plot_data(self):
        # Setup Plot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        im = ax.imshow(self.gain[1,1,:,0], interpolation='nearest', aspect='auto', 
                   origin = 'lower')#, cmap=_cmap, norm=_norm)
                  
        fig.colorbar(im).set_label('phase(degrees)')
        #plt.title('Plot from ' + self.filename)
        
        self.current_axes = plt.axes([0.2, 0.01, 0.65, 0.03])
        self.current_slider = Slider(self.current_axes, 'Power', min(self.currents),
                                   max(self.currents), 
                            valinit=min(self.currents), valfmt = '%.7f A')
        plt.show()
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
        
        self.currents = np.array(infile['currents'])
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
            self.add_data_set(self.currents, self.sweep_freqs, self.sweep_powers, self.gain,
                                self.measurement_frequency, 
                                background = self.unpumped_data)
        infile.close()
        
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