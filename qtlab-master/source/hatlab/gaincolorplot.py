# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 09:21:07 2016

A module containing a class to create a color plot of gain based on the power 
and frequency.  It can plot from a properly formatted h5py file, directly from
a flux_and_gain_sweep module, or from data added directly.

@author: HATLAB : Erick Brindock
"""
import h5py

import matplotlib.pyplot as plt
import matplotlib.colors as color
from matplotlib.widgets import Cursor
from matplotlib.widgets import Slider
import numpy as np
from hatlab import linearfit
class GainSweepColorPlot(object):
    '''
    Creates a color plot of a flux_and_gain_sweep. The x axis is the 
    frequency. The y axis is the pump power. The color represents the gain.
    This plot contains two sliders. One changes the data displayed based on the
    pump frequency. The other changes the data based on the flux.
    '''
    def __init__(self, filename = None):
        '''
        Method used to initialize the GainSweepColorPlot class
            Keyword Args:
                filename (string) : the path and filename of an h5py file 
                containing the data of a flux_and_gain_sweep
        '''
        if filename is not None:
            self.load_data_from_file(filename)
        else:
            print 'Class instantiated with no data'
           
    def plot_data(self):
        '''
        Sets up and plots the data loaded into the class
        '''
        # Setup ColorPlot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        colors=[color.hex2color('#000000'), color.hex2color('#FFFF00')]
        _cmap=color.LinearSegmentedColormap.from_list('my_cmap', colors)
        _norm=color.Normalize(vmin=-10, vmax=30)
        self.im = self.ax.imshow(self.gain[0,0,:,0], interpolation='nearest', aspect='auto', 
                   origin = 'lower', cmap=_cmap, norm=_norm)
        plt.gcf().subplots_adjust(left = .1, right = .95,top = .9, bottom = .15)
        plt.title('Plot from ' + self.filename)
        self.fig.colorbar(self.im).set_label('Gain (dB)')
        
        # Y-axis setup
        y_labels = np.linspace(self.sweep_powers[0], self.sweep_powers[-1], len(self.sweep_powers))
        y_loc = np.arange(len(y_labels))
        plt.yticks(y_loc, y_labels)
        plt.ylabel('Pump Power (dB)')
        # X-axis setup
        x_labels = ['%.4f'%num for num in np.linspace(self.measurement_frequency[0,0], self.measurement_frequency[0,-1], 11)/1e9]
        x_loc = [float(1601)/10*float(val) for val in range(len(x_labels))]
        plt.xticks(x_loc, x_labels)
        plt.xlabel('Pump frequency (GHz)')
        # Slider setup
        self.current_axes = plt.axes([0.1, 0.05, 0.65, 0.03])
        self.current_slider = Slider(self.current_axes, 'Power', min(self.currents),
                                   max(self.currents), 
                            valinit=min(self.currents), valfmt = '%.7f A')
        self.current_slider.on_changed(self.update)
        self.frequency_axes = plt.axes([0.1, 0.01, 0.65, 0.03])
        self.frequency_slider = Slider(self.frequency_axes, 'Frequency', min(self.sweep_freqs),
                                   max(self.sweep_freqs), 
                            valinit=min(self.sweep_freqs), valfmt = '%.0f Hz')
        self.frequency_slider.on_changed(self.update)
        self.cursor = Cursor(self.ax, useblit=True, color ='white', linewidth = 1)
        self.findex = 0
        self.cindex = 0
        def format_coord(x,y):
            '''
            Changes the corner text to give the data behind the point the 
            cursor is hovering over
                Args:
                    x (float) : the x coordinate
                    y (float) : the y coordinate
            '''
            frequency_index = int(x+.5)
            if frequency_index >= len(self.measurement_frequency):
                frequency_index = len(self.measurement_frequency) - 1
            frequency = self.measurement_frequency[self.cindex,frequency_index]/1e9
            sweep_index = int(y+.5)
            if sweep_index >= len(self.sweep_powers):
                sweep_index = len(self.sweep_powers)-1
            power = self.sweep_powers[sweep_index]
            gain = self.gain[self.cindex, self.findex, sweep_index, 0, frequency_index]
            return ('Power = {} dBm, Frequency = {} GHz, gain = {}'.format(power, frequency, gain))
        self.ax.format_coord = format_coord
        plt.show()
        
    def update(self, val):
        '''
        Called by the sliders when changed to update the data displayed by the 
        main plot.
            Args:
                val (float) : the current value of the slider
        '''
        cval = self.current_slider.val
        fval = self.frequency_slider.val
        currents = np.copy(self.currents).tolist()
        sweep_freqs = np.copy(self.sweep_freqs).tolist()
        self.cindex = currents.index(min(self.currents, key=lambda x:abs(x-cval)))
        self.findex = sweep_freqs.index(min(self.sweep_freqs, key=lambda x:abs(x-fval)))
        self.im.set_data(self.gain[self.cindex,self.findex,:,0])
        if (self.current_slider.val != self.currents[self.cindex]):
            self.current_slider.set_val(self.currents[self.cindex])
        if (self.frequency_slider.val != self.sweep_freqs[self.findex]):
            self.frequency_slider.set_val(self.sweep_freqs[self.findex])
            
            
    def plot_data_from_sweep(self, sweep):
        '''
        Plots data directly from a flux_and_gain_sweep module.
            Args:
                sweep (flux_and_gain_sweep) : the reference to the module
        '''
        self.gain = np.copy(sweep.SWEEP_DATA)
        self.add_data_set(sweep.CURRENTS,sweep.FREQUENCIES, sweep.POWERS, sweep.SWEEP_DATA,
                          sweep.MEASURE_BANDWIDTH, 
                          background = sweep.NORMALIZE_DATA,
                          dataname = sweep.__name__)
        self.plot_data()
        
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
        self.filename = filename.split('\\')[-1]
        infile = h5py.File(filename, 'r')
        if normalized:
            background = None
        else:
            background = np.array(infile['normal_data']) 
        self.add_data_set(np.array(infile['currents']),
                          np.array(infile['pump_frequencies']),
                          np.array(infile['pump_powers']),
                          np.array(infile['sweep_data']),
                          np.array(infile['measure_frequencies']),
                          background = background,
                          dataname = self.filename)
#        self.sweep_freqs = np.array(infile['pump_frequencies'])
#        self.sweep_powers = np.array(infile['pump_powers'])
#        
#        self.currents = np.array(infile['currents'])
#        self.gain = np.array(infile['sweep_data'])
#        self.measurement_frequency = np.array(infile['measure_frequencies'])
#        if normalized:
#            self.add_data_set(self.sweep_freqs, self.sweep_powers, self.gain,
#                                self.measurement_frequency)
#        else:
#            print type(self)
#            self.unpumped_data = np.array(infile['normal_data'])
#            self.add_data_set(self.currents, self.sweep_freqs, self.sweep_powers, self.gain,
#                                self.measurement_frequency, 
#                                background = self.unpumped_data)
        infile.close()
        
    def add_data_set(self, currents, frequencies, powers, gains, measurement_frequencies, 
                     background = None, dataname = 'Entered Data'):
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
        self.currents = currents
        self.sweep_freqs = frequencies
        self.sweep_powers = powers
        self.gain = np.copy(gains)
#        if background is None:
#            self.gain = np.copy(gains)
#        else:
        if background is not None:
            self.normalize_data(background)
        self.measurement_frequency = measurement_frequencies
        self.filename = dataname
#        self.currents = currents.tolist()
#        self.sweep_freqs = frequencies.tolist()
#        self.sweep_powers = powers.tolist()
#        if background is None:
#            self.gain = np.copy(gains)
#        else:
#            self.normalize_data(background)
#        self.measurement_frequency = measurement_frequencies
    
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
            
    def fit_data(self):
        for ci in range(self.gain.shape[0]):
            for fi in range(self.gain.shape[1]):
                for pi in range(self.gain.shape[2]):
                    self.gain[ci, fi, pi,0] = linearfit.fit_data(self.gain[ci,fi,pi,0], self.measurement_frequency[0])