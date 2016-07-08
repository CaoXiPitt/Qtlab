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

from instrument import Instrument 
from instruments import Instruments

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
# get original VNA settings
init_fstart = VNA.get_fstart()
init_fstop = VNA.get_fstop()
init_ifbw = VNA.get_ifbw()
init_trform = VNA.get_trform()
init_num_averages = VNA.get_avgnum()
init_elec_delay = VNA.get_electrical_delay()
# set VNA parameters
VNA.set_fstart(start)
VNA.set_fstop(stop)
VNA.set_ifbw(IF)
VNA.set_trform(trform)
VNA.set_electrical_delay(ELECTRICAL_DELAY)
GEN = qt.instruments.get('GEN')

h5py_filepath = 'C:\\Qtlab\\gain_sweep_data\\'
now = dt.datetime.now()
date_time = '{month}_{day}_{year}_{hour}'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour)
h5py_filename = 'JPC_pump_sweep_' + date_time #JPC_gain_ + date_time

powers = []
if POWER_STEP>0:
    value = MIN_POWER
    while value < MAX_POWER:
        powers.append(value)
        value += POWER_STEP
    powers.append(value)
else:
    value = MAX_POWER
    while value > MIN_POWER:
        powers.append(value)
        value += POWER_STEP
    powers.append(value)
powers = np.array(powers)

frequencies = []
if FREQUENCY_STEP>0:
    value = MIN_PUMP_FREQUENCY
    while value < MAX_PUMP_FREQUENCY:
        frequencies.append(value)
        value += PUMP_FREQUENCY_STEP
    frequencies.append(MAX_PUMP_FREQUENCY)
else:
    value = MAX_PUMP_FREQUENCY
    while value > MIN_PUMP_FREQUENCY:
        frequencies.append(value)
        value += PUMP_FREQUENCY_STEP
    frequencies.append(MIN_PUMP_FREQUENCY)
frequencies = np.array(frequencies)
 #frequencies = np.arange(MIN_PUMP_FREQUENCY, MAX_PUMP_FREQUENCY,)   
fp = h5py.File(h5py_filepath + h5py_filename, 'w')

fp.create_dataset('frequencies', data = frequencies)
fp.create_dataset('powers', data = powers)

#Get data to normalize
GEN.set_output_status(0)
VNA.average(num_averages, wait)
NORMALIZE_DATA = VNA.gettrace()
fp.create_dataset('freq_norm', data = NORMALIZE_DATA)
GEN.set_output_status(1)

for frequency in frequencies: 
    GEN.set_frequency(frequency)    
    for power in powers:
        GEN.set_power(power)
        #TODO get trace data
        print ('Power = {}dBm, Frequency = {}GHz'.format(power-20, frequency/1e9))
        VNA.average(num_averages, wait)
        fdata  = VNA.getfdata()
        fp.create_dataset('fdata_{}_{}'.format(power, frequency), data = fdata)
        trace_data = VNA.gettrace()
        fp.create_dataset('trace_data_{}_{}'.format(power, frequency), data = trace_data)

GEN.set_power(-20)        
fp.close()
        