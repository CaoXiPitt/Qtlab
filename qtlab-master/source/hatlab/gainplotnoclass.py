# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:30:18 2016

A module containing a class to create a line plot of gain vs frequency. It has 
sliders to choose the current, frequency, and power data to be displayed.  The 
data can be loaded from a properly formatted h5py file, directly from a 
flux_and_gain_sweep module, or from entered data.
 
@author: HATLAB : Erick Brindock
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import h5py
import numpy as np
from hatlab import linearfit
#import gainsweep as sweep


currents = None
sweep_freqs = None
sweep_powers = None
gain = None
measurement_frequency = None

def add_data_set(currents_data, frequencies_data, powers_data, gains_data, measurement_frequencies_data, background = None):
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
    global currents
    currents = currents_data.tolist()
    global sweep_freqs
    sweep_freqs = frequencies_data.tolist()
    global sweep_powers
    sweep_powers = powers_data.tolist()
    global gain
    if background is None:
        gain = np.copy(gains_data)
    else:
        normalize_data(background)
    global measurement_frequency
    measurement_frequency = measurement_frequencies_data
    
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

def plot_data_from_sweep(sweep):
    '''
    Plots data directly from a flux_and_gain_sweep module
    '''
    global gain
    gain = np.copy(sweep.SWEEP_DATA)
    add_data_set(sweep.CURRENTS,sweep.FREQUENCIES, sweep.POWERS, sweep.SWEEP_DATA,
                      sweep.MEASURE_BANDWIDTH, 
                      background = sweep.NORMALIZE_DATA)
    plot_data()
    
def plot_data(number):
    '''
    Sets up the plot window, adds sliders to the plot and displays it
    '''
    # Main Data Plot Setup
    figure = plt.figure(number)
    data_plot, = plt.plot(measurement_frequency[0], 
                               gain[0,0,0,0], 'k',label = "Normalized Data")  #added another 0
    fit_plot, = plt.plot(measurement_frequency[0], 
                              linearfit.fit_data(gain[0,0,0,0], 
                                                 measurement_frequency[0]), 
                              'r', label = 'Linear Fit Data', linewidth = 2)                       
    plt.axis([measurement_frequency[0,0], measurement_frequency[0,-1], -5, 35])
    plt.legend(handles = [data_plot, fit_plot])
    text = plt.text(0.01, 0.9,
                         to_string(gain[0,0,0,0], 
                                        linearfit.fit_data(gain[0,0,0,0],measurement_frequency[0])),
                    bbox=dict(facecolor='white', alpha=0.5), transform = plt.gca().transAxes)
    plt.gcf().subplots_adjust(left = .05, right = .95,top = .95, bottom = .15)
    axes = plt.gca()
    axes.set_xlim(measurement_frequency[0,0], measurement_frequency[0,-1])
    plt.title('Power and Frequency Sweep')
    plt.xlabel('Frequency (Ghz)')
    plt.ylabel('Gain (dB)')
    # Slider Setup
    freq_axes = plt.axes([0.2, 0.05, 0.65, 0.03])
    freq_slider = Slider(freq_axes, 'Frequency', 
                              min(sweep_freqs), max(sweep_freqs),
                         valinit=min(sweep_freqs), valfmt = '%.0f Hz')
    power_axes = plt.axes([0.2, 0.09, 0.65, 0.03])
    power_slider = Slider(power_axes, 'Power', min(sweep_powers),
                               max(sweep_powers), 
                        valinit=min(sweep_powers), valfmt = '%.1f dBm')
    current_axes = plt.axes([0.2, 0.01, 0.65, 0.03])
    current_slider = Slider(current_axes, 'Current', min(currents),
                               max(currents), 
                        valinit=min(currents), valfmt = '%.7f A')
                        
    def update(val):
        '''
        Updates the data plotted when the sliders are changed
            Input:
                val : the value passed in from the slider
        '''
        sval = int(power_slider.val*10)/10.0
        fval = freq_slider.val
        cval = current_slider.val
        findex = sweep_freqs.index(min(sweep_freqs, key=lambda x:abs(x-fval)))
        pindex = sweep_powers.index(min(sweep_powers, key=lambda x:abs(x-sval)))
        cindex = currents.index(min(currents, key=lambda x:abs(x-cval)))
        data_plot.set_ydata(gain[cindex][findex][pindex][0])
        data_plot.set_xdata(measurement_frequency[cindex])
        fit = linearfit.fit_data(gain[cindex,findex,pindex,0], measurement_frequency[cindex])
        #fit_plot.set_ydata(linearfit.fit_data(gain[cindex, findex, pindex, 0], measurement_frequency[0]))
        fit_plot.set_ydata(fit)
        fit_plot.set_xdata(measurement_frequency[cindex])
        text.set_text(to_string(gain[cindex,findex,pindex,0],fit))
        axes.set_xlim(measurement_frequency[cindex,0], measurement_frequency[cindex,-1])
        if (power_slider.val != sweep_powers[pindex]):
            power_slider.set_val(sweep_powers[pindex])
        if (freq_slider.val != sweep_freqs[findex]):
            freq_slider.set_val(sweep_freqs[findex])
        if (current_slider.val != currents[cindex]):
            current_slider.set_val(currents[cindex])
            
    current_slider.on_changed(update)
    power_slider.on_changed(update)
    freq_slider.on_changed(update)
    #plt.show()
    return figure
    


def to_string(measure, fit):
    return "Max. Measured Gain = {} dB"\
        "\nMax. Fit Gain = {} dB".format(np.amax(measure), np.amax(fit))             
    
def normalize_data(background):
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
    global gain
    for i in range(gain.shape[0]):
        gain[i] = gain[i]- background[i]
def load_data_from_file(filename, normalized = False):
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
    sweep_freqs = np.array(infile['pump_frequencies'])
    sweep_powers = np.array(infile['pump_powers'])
    
    currents = np.array(infile['currents'])
#        for i in range(len(self.sweep_powers)):  # Remove floating point error
#            self.sweep_powers[i] = int(self.sweep_powers[i]*10)/10.0
    global gain
    gain = np.array(infile['sweep_data'])
    measurement_frequency = np.array(infile['measure_frequencies'])
    if normalized:
        add_data_set(sweep_freqs, sweep_powers, gain,
                            measurement_frequency)
    else:
        unpumped_data = np.array(infile['normal_data'])
        add_data_set(currents, sweep_freqs, sweep_powers, gain,
                            measurement_frequency, 
                            background = unpumped_data)
    infile.close()