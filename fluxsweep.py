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
MAX_CURRENT = .2e-3 #Ampere         1e-3  previous
CURRENT_STEP = .05e-3 #Ampere    .0025e-3 previous
RAMP_RATE = .01 #Ampere/second
yoko_program_file_name = 'fluxsweep.csv'
start = 8.8e9 #Hz
stop =9.2e9 #Hz
IF = 3e3 #Hz
num_averages = 12 #Counts
wait = .6*num_averages #seconds (.6*num_averages? [for IF=3e3])
#trform = 'PLOG'
trform = 'PHAS'
phase_offset = 220
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
    
# Get original parameters VNA
init_fstart = VNA.get_fstart()
init_fstop = VNA.get_fstop()
init_ifbw = VNA.get_ifbw()
init_trform = VNA.get_trform()
init_num_averages = VNA.get_avgnum()
init_phase_offset = VNA.get_phase_offset()
# Get original parameters YOKO
old_ramp_time = YOKO.get_slope_interval()
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
    global old_ramp_time
    old_ramp_time = YOKO.get_slope_interval()

ramp_time = 30
def set_instrument_parameters():
    VNA.set_fstart(start)
    VNA.set_fstop(stop)
    VNA.set_ifbw(IF)
    VNA.set_trform(trform)
    VNA.set_phase_offset(phase_offset)
    # Set parameters YOKO
    global ramp_time
    ramp_time = YOKO.set_ramp_intervals(step = CURRENT_STEP, rate = RAMP_RATE)

currents = []
# Populate current values
def set_currents(min_current = MIN_CURRENT,
                    max_current = MAX_CURRENT,
                    current_step = CURRENT_STEP):
    '''
    Creates a list of currents to sweep through. (Note: if current_step is 
    negative it will count from max_current down to min_current)
    '''
    global currents
    if current_step>0:
        value = min_current
        while value < max_current:
            currents.append(value)
            value += current_step
        currents.append(max_current)
    else:
        value = max_current
        while value > min_current:
            currents.append(value)
            value += current_step
        currents.append(min_current)
    return currents

    
frequency_data = []
def ask_frequency_data():
    global frequency_data
    frequency_data = VNA.getfdata()
    
phase_data = [] 
def sweep_current(sweep_currents):
    global currents
    currents = sweep_currents    
    if (YOKO.get_output_level() != currents[0]):    
        time.sleep(YOKO.change_current(currents[0])) #set current to staritng value
    i = 0
    global phase_data
    phase_data = np.empty((len(currents), 1601))
    for current in currents:
        print ('Testing at %s Amps' %current)
        YOKO.change_current(current)
        time.sleep(ramp_time)    #wait for current to reach new value
        VNA.average(num_averages, wait)
        phase_data[i] = VNA.gettrace()[0]
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
    fp.create_dataset('trace_data', data=phase_data)
    fp.create_dataset('frequency_data', data=frequency_data)
    fp.create_dataset('current_data', data = currents)    
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
    if sweep_currents is None:
        sweep_currents = set_currents()
    sweep_current(sweep_currents)
    ask_frequency_data()
    reset_instrument_state()
    save_data_to_h5py()
    plot = fluxplot.FluxSweepPlot(frequencies = frequency_data,
                                  currents = currents,
                                  phases = phase_data)
    plot.plot_data()
    
if __name__ == '__main__':
    run_sweep()        