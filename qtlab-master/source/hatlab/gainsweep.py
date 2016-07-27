# -*- coding: utf-8 -*-
"""
Created on Tue Jul 05 13:34:04 2016

@author: HATLAB
"""

import qt
import time
import datetime as dt
import h5py
import numpy as np

# Settings --------------------------------------------------------------------
VNA_NAME = 'VNA'
GEN_NAME = 'GEN'

MIN_POWER = -40 #dBm total power
MAX_POWER = -32 #dBm total power 
POWER_STEP = .2 #dbm
MIN_PUMP_FREQUENCY = 15.022871e9 #Hz
MAX_PUMP_FREQUENCY = 15.042871e9 #Hz
PUMP_FREQUENCY_STEP = .0025e9
MIN_MEASURE_FREQUENCY = 8.7919e9 #Hz
MAX_MEASURE_FREQUENCY = 8.8919e9 #Hz
FREQUENCY_STEP = 1e9 #Hz

MIN_POWER = MIN_POWER + 20 # factor in -20dB attenuator
MAX_POWER = MAX_POWER + 20 # factor in -20dB attenuator
start = MIN_MEASURE_FREQUENCY #Hz
stop =MAX_MEASURE_FREQUENCY #Hz
IF = 3e3 #Hz
num_averages = 24 #Counts
wait = .6*num_averages #seconds (.6*num_averages? [for IF=3e3])
trform = 'PLOG' #'MLOG'
ELECTRICAL_DELAY = 63e-9 #sec
# End of Settings -------------------------------------------------------------     
VNA = None
GEN = None
def get_instruments(name = VNA_NAME):
    global VNA
    VNA = qt.instruments.get(name)
    global GEN
    GEN = qt.instruments.get(GEN_NAME)

# get original VNA settings
init_fstart = VNA.get_fstart()
init_fstop = VNA.get_fstop()
init_ifbw = VNA.get_ifbw()
init_trform = VNA.get_trform()
init_num_averages = VNA.get_avgnum()
init_elec_delay = VNA.get_electrical_delay()

def store_instrument_parameters():
    '''
    Stores the instrument settings so they can be reset later
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
    global init_elec_delay
    init_elec_delay = VNA.get_electrical_delay()
    
def set_instrument_parameters():
    '''
    Sets the instruments to the #Settings values for the test to be run
    '''
    # set VNA parameters
    VNA.set_fstart(start)
    VNA.set_fstop(stop)
    VNA.set_ifbw(IF)
    VNA.set_trform(trform)
    VNA.set_electrical_delay(ELECTRICAL_DELAY)

#h5py_filepath = 'C:\\Qtlab\\gain_sweep_data\\'
#now = dt.datetime.now()
#date_time = '{month}_{day}_{year}_{hour}'.format(month = now.month,
#                                                        day = now.day,
#                                                        year = now.year,
#                                                        hour = now.hour)
#h5py_filename = 'JPC_pump_sweep_' + date_time #JPC_gain_ + date_time

POWERS = np.append(np.arange(MIN_POWER, MAX_POWER, POWER_STEP), MAX_POWER)
def set_powers(powers = POWERS):
    '''
    Populates a list of powers to be swept through
        Args:
            powers (numpy array) : powers to be swept through
    '''
    global POWERS
    POWERS = powers.tolist()
    
FREQUENCIES = np.append(np.arange(MIN_PUMP_FREQUENCY, 
                                  MAX_PUMP_FREQUENCY, 
                                  PUMP_FREQUENCY_STEP), 
                        MAX_PUMP_FREQUENCY)
def set_frequencies(frequencies = FREQUENCIES):
    '''
    Populates a list of frequencies to be swept through
        Args:
            frequencies (numpy array) : frequencies to be swept through
    '''
    global FREQUENCIES
    FREQUENCIES = frequencies.tolist()
    
#fp = h5py.File(h5py_filepath + h5py_filename, 'w')

#fp.create_dataset('pump_frequencies', data = FREQUENCIES)
#fp.create_dataset('pump_powers', data = POWERS)

#Get data to normalize
NORMALIZE_DATA = []
#fp.create_dataset('freq_norm', data = NORMALIZE_DATA)
def get_normalization_data(index):
    '''
    Gets a data trace without the pump being on to use to normalize raw data
    '''
    GEN.set_output_status(0)
    VNA.average(num_averages, wait)
    global NORMALIZE_DATA
    NORMALIZE_DATA[index] = VNA.gettrace()
    GEN.set_output_status(1)

MEASURED_FREQUENCIES = []
SWEEP_DATA = []
def sweep_power_and_frequency():
    '''
    Runs the sweep over the powers and frequencies specified in the #Settings 
    or set via set_frequencies/ set_powers.  The data is saved to SWEEP_DATA in 
    the form [frequency_index][power_index][data]. The frequencies of the trace 
    are saved to MEASURED_FREQUENCIES  
    '''
    #TODO update to make compatable with new h5py data format
    
    global FREQUENCIES
    global POWERS
    global MEASURED_FREQUENCIES
    MEASURED_FREQUENCIES = VNA.getfdata().tolist()
    num_tests = len(FREQUENCIES)*len(POWERS)
    print('Number of tests = {}. Time per test = {} sec. Total time ~ {} min'
                                .format(num_tests, wait, num_tests*wait/60))
    global SWEEP_DATA
    SWEEP_DATA = np.empty((len(FREQUENCIES),
                           len(POWERS), 2,   # added 2
                            len(MEASURED_FREQUENCIES)))
    global NORMALIZE_DATA
    NORMALIZE_DATA = np.empty((len(FREQUENCIES), 2, len(MEASURED_FREQUENCIES)))  #added 2
    for fi in range(len(FREQUENCIES)): 
        GEN.set_frequency(FREQUENCIES[fi])
        get_normalization_data(fi)
        for pi in range(len(POWERS)):
            GEN.set_power(POWERS[pi])
            print ('Power = {}dBm, Frequency = {}GHz, #{}/{}'
                                .format(POWERS[pi]-20, FREQUENCIES[fi]/1e9, 
                                        pi+fi*len(POWERS)+1, num_tests))
            VNA.average(num_averages, wait)
            trace_data = VNA.gettrace()
            SWEEP_DATA[fi][pi] = trace_data #[0]
    GEN.set_power(-20)
def save_data_to_h5py(filename):
    '''
    Saves the most recent data to an h5py file.
        Args:
            filename (string) : the file to be saved to (note: must include the
            path)
            this will default to 
            C:\Qtlab\gain_sweep_data\JPC_pump_sweep_{month}_{day}_{year}_{hour}
            if no name is specified
    '''
    h5py_filepath = 'C:\\Qtlab\\gain_sweep_data\\'
    if filename is None: 
        now = dt.datetime.now()
        date_time = '{month}_{day}_{year}_{hour}:{minute}'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour,
                                                        minute = now.minute)
        h5py_filename = 'JPC_pump_sweep_' + date_time
        filename = h5py_filepath + h5py_filename
    else:
        filename = h5py_filepath + filename
    outfile = h5py.File(filename, 'w')
    outfile.create_dataset('pump_frequencies', data = FREQUENCIES)
    outfile.create_dataset('pump_powers', data = POWERS)
    outfile.create_dataset('normal_data', data = NORMALIZE_DATA)
    outfile.create_dataset('sweep_data', data = SWEEP_DATA)
    outfile.create_dataset('measure_frequencies', data = MEASURED_FREQUENCIES)        
    outfile.close()
def reset_instrument_state():
    '''
    Resets the instruments to their original states. To be used after the test
    is run.
    '''
    VNA.set_fstart(init_fstart)
    VNA.set_fstop(init_fstop)
    VNA.set_ifbw(init_ifbw)
    VNA.set_trform(init_trform)
    VNA.set_electrical_delay(init_elec_delay)
    
def run_sweep(filename = None):
    '''
    Command to initial instruments, set parameters, run sweep, save data, etc.
    This uses settings in #Settings or the most recent changes made by the set_
    methods
    '''
    get_instruments()
    store_instrument_parameters()
    set_instrument_parameters()
    set_powers()
    set_frequencies()
    #get_normalization_data()
    sweep_power_and_frequency()
    reset_instrument_state()
    save_data_to_h5py(filename)

if __name__ == '__main__':
    run_sweep()