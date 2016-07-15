# -*- coding: utf-8 -*-
"""
Created on Fri Jul 08 09:24:12 2016

@author: HATLAB : Erick Brindock
"""
import h5py

import matplotlib.pyplot as plt
import matplotlib.colors as color
from matplotlib.widgets import Cursor
import numpy as np

class FluxSweepPlot(object):
    def __init__(self, filename = None, frequencies = None, currents = None,
                 phases = None):
        if filename is not None:
            self.load_from_file(filename)
        elif (frequencies is not None and currents is not None and phases is not None):
            self.add_data_set(frequencies, currents, phases)
        else:
            print('Data must be loaded or added before plot can be made')

    def load_from_file(self, 
                h5py_filepath=
                'C:\\Qtlab\\flux_sweep_data\\signal_sweep_7_6_2016_11_6'):
        '''
        Loads data to be plotted from a file
            Input:
                h5py_filepath (string) : the filepath and file name to be loaded
        '''
        self.filename = h5py_filepath
        fp2 = h5py.File(self.filename, 'r')
        self.add_data_set(fp2['currents'][:],
                          fp2['measure_frequencies'][:],
                          fp2['sweep_data'][0:-1,1],
                          dataname = self.filename.split('\\')[-1])        
        fp2.close()
    #TODO correct plot from sweep    
    def plot_data_from_sweep(self, sweep):
        self.add_data_set(sweep.CURRENTS, 
                          sweep.MEASURE_BANDWIDTH, 
                          sweep.PHASE_DATA)
        self.plot_data()
    #TODO correct plot from data set    
    def add_data_set(self, currents, frequencies, phases, dataname = 'Entered Data'):
        self.ar_freq = frequencies
        self.ar_current_data = currents
        self.ar_phase = np.array(phases)
        self.filename = dataname
            
    def plot_data(self):
        # color map setting
        levels=[180, 90, 0, -90, -180]
        colors=[color.hex2color('#000000'), color.hex2color('#FF0000'), 
                color.hex2color('#FFFF00'), color.hex2color('#00FF00'),
                color.hex2color('#000000')]
        levels=levels[::-1]
        colors=colors[::-1]
        _cmap=color.LinearSegmentedColormap.from_list('my_cmap', colors)
        _norm=color.Normalize(vmin=-180, vmax=180)
        
        
        if self.ar_current_data[0] > self.ar_current_data[-1]:
            self.ar_phase = self.ar_phase[::-1]
            
        # Setup Plot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        im = ax.imshow(self.ar_phase.transpose(), interpolation='nearest', aspect='auto', 
                   origin = 'lower', cmap=_cmap, norm=_norm)
                  
        fig.colorbar(im).set_label('phase(degrees)')
        plt.title('Plot from ' + self.filename)
        
        # Y axis setup
        #TODO correct y axis for variable numbers of y values
        y_labels = np.linspace(self.ar_freq[0], self.ar_freq[-1], 21)/1e9
        y_loc = [float(1601)/20*float(val) for val in range(len(y_labels))]
        plt.yticks(np.array(y_loc), y_labels)
        plt.ylabel('frequency(GHz)')
        
        # X axis setup
        num_x_ticks = 20
        if len(self.ar_current_data) < num_x_ticks:
            num_x_ticks = 1
        x_labels = np.arange(self.ar_current_data[0], self.ar_current_data[-1], 
                            (self.ar_current_data[-1] - self.ar_current_data[0])/num_x_ticks)
        x_loc = [len(self.ar_current_data)/float(num_x_ticks)*i for i in range(num_x_ticks)]
        plt.xticks(x_loc, x_labels*1000, rotation=90)
#        plt.xticks(x_loc, x_labels, rotation=90)
        plt.xlabel('Current (mA)')
#       plt.xlabel('Time elapsed (minutes)')
        
        self.cursor = Cursor(ax, useblit=True, color ='white', linewidth = 1)
        def format_coord(x,y):
            current = self.ar_current_data[int(x)]*100
            frequency = self.ar_freq[int(y)]/1e9
            phase = self.ar_phase[int(x+.5)][int(y+.5)]
            return ('Current = {} mA, Frequency = {} GHz, Phase = {}'.format(current, frequency, phase))
        ax.format_coord = format_coord
        plt.show()
        
    def get_data_point(self):
        return [self.ar_freq[0], self.ar_current_data[0], self.ar_phase[0][0]]