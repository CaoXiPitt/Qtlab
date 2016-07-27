# -*- coding: utf-8 -*-
"""
A module containg the data and methods needed to perform flux sweeps.  It can 
be run as a stand alone module (ie. execfile(%PATH%\fluxsweep.py) in Qtlab), 
using the settings under the # Settings heading.  It can also be imported so 
certain  parameters can be changed and the test run and rerun.  The parameters 
that cna be changed are the filename, whether the data is saved or not, and the
currents to be swpet through.

@author: Hatlab : Erick Brindock
"""
import qt
import time
import datetime as dt
import h5py
import matplotlib.pyplot as plt
import matplotlib.colors as color
import matplotlib
import sys
import fluxplot
import numpy as np

# Settings --------------------------------------------------------------------
VNA_NAME = 'VNA'
CS_NAME = 'YOKO'
MIN_CURRENT = 0e-3 #Ampere
MAX_CURRENT = .5e-3 #Ampere         1e-3  previous
CURRENT_STEP = -.005e-3 #Ampere    .0025e-3 previous
RAMP_RATE = .01 #Ampere/second
YOKO_PROGRAM_FILE_NAME = 'fluxsweep.csv'
START = 4e9 #Hz
STOP =8e9 #Hz
IF = 3e3 #Hz
NUM_AVERAGES = 12 #Counts
#trform = 'PLOG'
trform = 'PLOG'
PHASE_OFFSET = -180
TRIGGER_SOURCE = 'bus'
AVG_TRIGGER = 1
h5py_filepath = 'C:\\Qtlab\\flux_sweep_data\\'
now = dt.datetime.now()
date_time = '{month}_{day}_{year}_{hour}_{minute}'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour,
                                                        minute = now.minute)
h5py_filename = 'signal_sweep_' + date_time
# End of Settings -------------------------------------------------------------

# Get Instruments
VNA = qt.instruments.get('VNA')
YOKO = qt.instruments.get('YOKO')
def get_instruments(vna_name = VNA_NAME, cs_name = CS_NAME):
    '''
    Gets references to the instruments used in the sweep
        Args:
            vna_name (string) : the name of the VNA as it appears in Qtlab
            cs_name (strint) : the name of the current source as it appears in 
            Qtlab
    '''
    global VNA
    VNA = qt.instruments.get(vna_name)
    global YOKO
    YOKO = qt.instruments.get(cs_name)
    

init_fstart = None
init_fstop = None
init_ifbw = None
init_trform = None
init_num_averages = None
init_phase_offset = None
init_trigger_source = None
init_avg_trigger = None
old_ramp_time = None
def store_instrument_parameters():
    '''
    Saves the original state of the instruments so the can be reset after the 
    test is complete
    '''
    global init_fstart
    init_fstart = VNA.get_fstart()
    global init_fstop
    init_fstop = VNA.get_fstop()
    global init_ifbw
    init_ifbw = VNA.get_ifbw()
    global init_trform
    init_trform = VNA.get_trform()
    global init_num_averages
    init_num_averages = VNA.get_avgnum()
    global init_phase_offset
    init_phase_offset = VNA.get_phase_offset()
    global init_trigger_source
    init_trigger_source = VNA.get_trigger_source()
    global init_avg_trigger
    init_avg_trigger = VNA.get_avg_trigger()    
    global old_ramp_time
    old_ramp_time = YOKO.get_slope_interval()

ramp_time = 30
def set_instrument_parameters():
    '''
    Sets the instrument parameters to those specified in the  # Settings 
    section, so the sweep can be run.
    '''
    VNA.set_fstart(START)
    VNA.set_fstop(STOP)
    VNA.set_ifbw(IF)
    VNA.set_trform(trform)
    VNA.set_phase_offset(PHASE_OFFSET)
    VNA.set_trigger_source(TRIGGER_SOURCE)
    VNA.set_avg_trigger(AVG_TRIGGER)
    # Set parameters YOKO
    global ramp_time
    ramp_time = YOKO.set_ramp_intervals(step = CURRENT_STEP, rate = RAMP_RATE)

CURRENTS = []
# Populate current values
def set_currents(currents):
    '''
    Creates a list of currents to sweep through. (Note: if current_step is 
    negative it will count from max_current down to min_current)
        Args:
            currents (nparray) : an array of currents to be run through (note: 
            setting this value to None will use the # Settings parameters)
    '''
    global CURRENTS
    if currents is None:
        CURRENTS = np.append(np.arange(MIN_CURRENT, 
                                       MAX_CURRENT, 
                                       abs(CURRENT_STEP)),
                             MAX_CURRENT)
        if (CURRENT_STEP<0):
            CURRENTS[::-1] 
    else:
        CURRENTS = currents

def set_measure_bandwidth(start, stop):
    VNA.set_fstart(start)
    VNA.set_fstop(stop)
    
MEASURE_BANDWIDTH = []
def get_frequency_data():
    '''
    Gets the frequencies the VNA is measuring
    '''
    global MEASURE_BANDWIDTH
    MEASURE_BANDWIDTH = VNA.getfdata()
    
PHASE_DATA = [] 
def sweep_current(plot = True):
    '''
    Sweeps over the currents in the module and prints out the current used in 
    the test. It also prints the resonant frequency at the current
    '''    
    if (YOKO.get_output_level() != CURRENTS[0]):    
        time.sleep(YOKO.change_current(CURRENTS[0])) #set current to staritng value
    i = 0
    global PHASE_DATA
    PHASE_DATA = np.zeros((len(CURRENTS), 2, 1601))-180  #TODO changed to zeros and subtract 180
    print type(PHASE_DATA[:,0,:])
    print CURRENTS[0]
    if plot:
            setup_plot()
    for current in CURRENTS:
        print ('Testing at %s Amps' %current)
        YOKO.change_current(current)
        time.sleep(ramp_time)    #wait for current to reach new value
        VNA.average(NUM_AVERAGES)
        PHASE_DATA[i] = VNA.gettrace()
        i+=1
        if plot:
            try:
                IMAGE.set_array(PHASE_DATA[:,0,:].transpose())
                plt.set_title('Running Sweep at %s mA' %current*1000)
                plt.pause(.01)
            except:
                print'failed2'
        print 'Test {}. Resonant frequency = {}'.format(i, get_resonant_frequency(current))
        

def save_data_to_h5py(filename = None):
    '''
    Saves the data from a sweep to an h5py file.
        Optional Args:
            filename (string) : the path and filename to save the file to.
            (note: This will default to C:\Qtlab\flux_sweep_data\
            signal_sweep_{month}_{day}_{year}_{hour}_{minute})
    '''
    if filename is None:
        h5py_filepath = 'C:\\Qtlab\\flux_sweep_data\\'
        now = dt.datetime.now()
        date_time = '{month}_{day}_{year}_{hour}_{minute}'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour,
                                                        minute = now.minute)
        h5py_filename = 'signal_sweep_' + date_time
        filename = h5py_filepath + h5py_filename
    fp = h5py.File(filename, 'w')
    fp.create_dataset('sweep_data', data=PHASE_DATA)
    fp.create_dataset('measure_frequencies', data=MEASURE_BANDWIDTH)
    fp.create_dataset('currents', data = CURRENTS)    
    fp.close()
    
def reset_instrument_state():
    '''
    Resets the intruments to their original parameters
    '''
    VNA.set_fstart(init_fstart)
    VNA.set_fstop(init_fstop)
    VNA.set_ifbw(init_ifbw)
    VNA.set_trform(init_trform)
    VNA.set_avgnum(init_num_averages)
    VNA.set_phase_offset(init_phase_offset)
    VNA.set_trigger_source(init_trigger_source)
    VNA.set_avg_trigger(init_avg_trigger)
    YOKO.set_slope_interval(old_ramp_time)
IMAGE = None
def setup_plot():
    try:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.ion()
        # color map setting
        levels=[180, 90, 0, -90, -180]
        colors=[color.hex2color('#000000'), color.hex2color('#FF0000'), 
                color.hex2color('#FFFF00'), color.hex2color('#00FF00'),
                color.hex2color('#000000')]
        levels=levels[::-1]
        colors=colors[::-1]
        _cmap=color.LinearSegmentedColormap.from_list('my_cmap', colors)
        _norm=color.Normalize(vmin=-180, vmax=180)
        print "one"
        global IMAGE
        IMAGE = ax.imshow(PHASE_DATA[:,0,:].transpose(), interpolation='nearest', 
                          aspect='auto', origin = 'lower', cmap=_cmap, norm=_norm, 
                          extent = [CURRENTS[0],CURRENTS[-1], 
                                    MEASURE_BANDWIDTH[0], MEASURE_BANDWIDTH[-1]])
        print 'two'
        ax.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(numticks = 15))
        ax.xaxis.set_major_locator(matplotlib.ticker.LinearLocator(numticks = 6))
        plt.title('Running Sweep')
        fig.colorbar(IMAGE).set_label('phase(degrees)')
        plt.xticks(rotation = 90, valfmt = '%.5f')
        plt.xlabel('Current (mA)')
        plt.tight_layout()
    except:
        print 'failed'
    
def run_sweep(sweep_currents = None, save_data = True, filename = None, 
              measure_bandwidth = None, plot = True):
    '''
    Performs the actual test. If the module is imported this is the only method 
    that actually needs to be called. It will get the instruments, set their 
    parameters, run the sweep, save the data, etc.
        Optional Args:
            sweep_currents (nparray) : a list of currents to sweep over
            save_data (boolean) : if true the data will be saved to an h5py file
            filename (string) : the path and filename to save the data to
            measure_bandwidth (2 element list) : [start, stop] values for the VNA measurement
    '''
    get_instruments()
    store_instrument_parameters()
    try:
        set_instrument_parameters()
        set_currents(sweep_currents)
        if measure_bandwidth is not None:
            set_measure_bandwidth(measure_bandwidth[0], measure_bandwidth[1])
        get_frequency_data()
        
        sweep_current(plot)
    finally:
        reset_instrument_state()
    if save_data:
        save_data_to_h5py(filename = filename)
#    plot = fluxplot.FluxSweepPlot(frequencies = MEASURE_BANDWIDTH,
#                                  currents = CURRENTS,
#                                  phases = PHASE_DATA)
#    plot.plot_data()
        
def get_resonant_frequency(current):
    '''
    A method to determine the resonant frequency at a specific current level
    If the measured frequencies are too broad, harmonics may result in 
    undesired behavior
        Args:
            current (float) : the current to measure the resonant frequency at
        Output:
            (float) : the resonant frequency of the mode
    '''
    index = np.where(np.absolute(CURRENTS - current) < .1e-9)
    abs_phase = np.absolute(PHASE_DATA)
    abs_min = np.amin(abs_phase[index])
    res_freq_index = np.where(abs_phase == abs_min)[2][0]
    return MEASURE_BANDWIDTH[res_freq_index]
if __name__ == '__main__':
    run_sweep(save_data = True)        