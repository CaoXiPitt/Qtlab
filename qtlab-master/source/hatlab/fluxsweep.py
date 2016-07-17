# -*- coding: utf-8 -*-
"""
A script file to do flux sweeps

@author: Hatlab : Erick Brindock
"""
import qt
import time
import datetime as dt
import h5py
import sys
import fluxplot
import numpy as np

# Settings
VNA_NAME = 'VNA'
CS_NAME = 'YOKO'
MIN_CURRENT = 0.1e-3 #Ampere
MAX_CURRENT = .25e-3 #Ampere         1e-3  previous
CURRENT_STEP = .05e-3 #Ampere    .0025e-3 previous
RAMP_RATE = .01 #Ampere/second
YOKO_PROGRAM_FILE_NAME = 'fluxsweep.csv'
START = 8.8e9 #Hz
STOP =9.2e9 #Hz
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


# Get Instruments
VNA = qt.instruments.get('VNA')
YOKO = qt.instruments.get('YOKO')
def get_instruments(vna_name = VNA_NAME, cs_name = CS_NAME):
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

    
MEASURE_BANDWIDTH = []
def ask_frequency_data():
    global MEASURE_BANDWIDTH
    MEASURE_BANDWIDTH = VNA.getfdata()
    
PHASE_DATA = [] 
def sweep_current():    
    if (YOKO.get_output_level() != CURRENTS[0]):    
        time.sleep(YOKO.change_current(CURRENTS[0])) #set current to staritng value
    i = 0
    global PHASE_DATA
    PHASE_DATA = np.empty((len(CURRENTS), 2, 1601))
    for current in CURRENTS:
        print ('Testing at %s Amps' %current)
        YOKO.change_current(current)
        time.sleep(ramp_time)    #wait for current to reach new value
        VNA.average(NUM_AVERAGES)
        PHASE_DATA[i] = VNA.gettrace()
        i+=1
        print 'test {}'.format(i)

def save_data_to_h5py(filename = None):
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
    VNA.set_fstart(init_fstart)
    VNA.set_fstop(init_fstop)
    VNA.set_ifbw(init_ifbw)
    VNA.set_trform(init_trform)
    VNA.set_avgnum(init_num_averages)
    VNA.set_phase_offset(init_phase_offset)
    YOKO.set_slope_interval(old_ramp_time)

def run_sweep(sweep_currents = None):
    get_instruments()
    store_instrument_parameters()
    set_instrument_parameters()
    set_currents(sweep_currents)
    sweep_current()
    ask_frequency_data()
    reset_instrument_state()
    save_data_to_h5py()
    plot = fluxplot.FluxSweepPlot(frequencies = MEASURE_BANDWIDTH,
                                  currents = CURRENTS,
                                  phases = PHASE_DATA)
    plot.plot_data()
    
if __name__ == '__main__':
    run_sweep()        