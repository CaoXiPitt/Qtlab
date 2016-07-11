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


vna_name = 'VNA'
signal_gen_name = 'GEN'

MIN_POWER = -40 #dBm total power
MAX_POWER = -32 #dBm total power 
POWER_STEP = 0.4 #dbm
MIN_PUMP_FREQUENCY = 14.982871e9 #Hz
MAX_PUMP_FREQUENCY = 15.082871e9 #Hz
PUMP_FREQUENCY_STEP = .005e9
MIN_MEASURE_FREQUENCY = 8.7919e9 #Hz
MAX_MEASURE_FREQUENCY = 8.8919e9 #Hz
FREQUENCY_STEP = 1e9 #Hz

MIN_POWER = MIN_POWER + 20 # factor in -20dB attenuator
MAX_POWER = MAX_POWER + 20 # factor in -20dB attenuator
start = MIN_MEASURE_FREQUENCY #Hz
stop =MAX_MEASURE_FREQUENCY #Hz
IF = 3e3 #Hz
num_averages = 12 #Counts
wait = .6*num_averages #seconds (.6*num_averages? [for IF=3e3])
#trform = 'PLOG'
trform = 'MLOG'
ELECTRICAL_DELAY = 63e-9 #sec
#PHASE_OFFSET =
     
VNA = qt.instruments.get('VNA')
GEN = qt.instruments.get('GEN')
def get_instruments(name = vna_name):
    global VNA
    VNA = qt.instruments.get(name)
    global GEN
    GEN = qt.instruments.get('GEN')

# get original VNA settings
init_fstart = VNA.get_fstart()
init_fstop = VNA.get_fstop()
init_ifbw = VNA.get_ifbw()
init_trform = VNA.get_trform()
init_num_averages = VNA.get_avgnum()
init_elec_delay = VNA.get_electrical_delay()

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
    global init_elec_delay
    init_elec_delay = VNA.get_electrical_delay()
    
def set_instrument_parameters():
    # set VNA parameters
    VNA.set_fstart(start)
    VNA.set_fstop(stop)
    VNA.set_ifbw(IF)
    VNA.set_trform(trform)
    VNA.set_electrical_delay(ELECTRICAL_DELAY)

h5py_filepath = 'C:\\Qtlab\\gain_sweep_data\\'
now = dt.datetime.now()
date_time = '{month}_{day}_{year}_{hour}'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour)
h5py_filename = 'JPC_pump_sweep_' + date_time #JPC_gain_ + date_time

POWERS = np.append(np.arange(MIN_POWER, MAX_POWER, POWER_STEP), MAX_POWER)
def set_powers(powers = POWERS):
    global POWERS
    POWERS = powers
    
FREQUENCIES = np.append(np.arange(MIN_PUMP_FREQUENCY, 
                                  MAX_PUMP_FREQUENCY, 
                                  PUMP_FREQUENCY_STEP), 
                        MAX_PUMP_FREQUENCY)
def set_frequencies(frequencies = FREQUENCIES):
    global FREQUENCIES
    FREQUENCIES = frequencies
    
fp = h5py.File(h5py_filepath + h5py_filename, 'w')

fp.create_dataset('pump_frequencies', data = FREQUENCIES)
fp.create_dataset('pump_powers', data = POWERS)

#Get data to normalize
NORMALIZE_DATA = []
fp.create_dataset('freq_norm', data = NORMALIZE_DATA)
def get_normalization_data():
    GEN.set_output_status(0)
    VNA.average(num_averages, wait)
    global NORMALIZE_DATA
    NORMALIZE_DATA = VNA.gettrace()
    GEN.set_output_status(1)

MEASURED_FREQUENCIES = []
#def run_sweep():
#    global FREQUENCIES
#    global POWERS
#    global MEASURED_FREQUENCIES
#    MEASURED_FREQUENCIES = VNA.getfdata()
#    for frequency in FREQUENCIES: 
#        GEN.set_frequency(frequency)    
#        for power in POWERS:
#            GEN.set_power(power)
#            #TODO get trace data
#            print ('Power = {}dBm, Frequency = {}GHz'.format(power-20, frequency/1e9))
#            VNA.average(num_averages, wait)
#            fdata  = VNA.getfdata()
#            fp.create_dataset('fdata_{}_{}'.format(power, frequency), data = fdata)
#            trace_data = VNA.gettrace()
#            fp.create_dataset('trace_data_{}_{}'.format(power, frequency), data = trace_data)
SWEEP_DATA = []
def sweep_power_and_frequency():
    global FREQUENCIES
    global POWERS
    global MEASURED_FREQUENCIES
    MEASURED_FREQUENCIES = VNA.getfdata()
    global SWEEP_DATA
    SWEEP_DATA = np.empty(len(FREQUENCIES), len(POWERS), len(MEASURED_FREQUENCIES))
    for fi in range(len(FREQUENCIES)): 
        GEN.set_frequency(FREQUENCIES[fi])    
        for pi in range(len(POWERS)):
            GEN.set_power(POWERS[pi])
            #TODO get trace data
            print ('Power = {}dBm, Frequency = {}GHz'.format(POWERS[pi]-20, FREQUENCIES[fi]/1e9))
            VNA.average(num_averages, wait)
            trace_data = VNA.gettrace()
            SWEEP_DATA[fi][pi] = trace_data[0]
    GEN.set_power(-20)
def save_data_to_h5py(filename = None):
    if filename is None:
        h5py_filepath = 'C:\\Qtlab\\gain_sweep_data\\'
        now = dt.datetime.now()
        date_time = '{month}_{day}_{year}_{hour}'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour)
        h5py_filename = 'JPC_pump_sweep_' + date_time #JPC_gain_ + date_time
        filename = h5py_filepath + h5py_filename
    outfile = h5py.File(filename, 'w')
    outfile.create_dataset('pump_frequencies', data = FREQUENCIES)
    outfile.create_dataset('pump_powers', data = POWERS)
    outfile.create_dataset('normal_frequencies', data = NORMALIZE_DATA)
    outfile.create_dataset('sweep_data', data = SWEEP_DATA)        
    outfile.close()
def reset_instrument_state():
    VNA.set_fstart(init_fstart)
    VNA.set_fstop(init_fstop)
    VNA.set_ifbw(init_ifbw)
    VNA.set_trform(init_trform)
    VNA.set_electrical_delay(init_elec_delay)
    
def run_sweep():
    get_instruments()
    store_instrument_parameters()
    set_instrument_parameters()
    set_powers()
    set_frequencies()
    get_normalization_data()
    sweep_power_and_frequency()
    reset_instrument_state()
    save_data_to_h5py()

if __name__ == '__main__':
    run_sweep()