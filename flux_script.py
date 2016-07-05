# -*- coding: utf-8 -*-
"""
A script file to do flux sweeps

@author: Hatlab : Erick Brindock
"""
import qt
import time
import datetime as dt
import h5py

from instrument import Instrument 
from instruments import Instruments
# Settings
vna_name = 'VNA'
cs_name = 'YOKO'
min_current = 0 #Ampere
max_current = .3e-3 #Ampere         1e-3  previous
current_step = .005e-3 #Ampere    .0025e-3 previous
ramp_rate = .01 #Ampere/second
yoko_program_file_name = 'fluxsweep.csv'
start = 7.6e9 #Hz
stop =9.2e9 #Hz
IF = 3e3 #Hz
num_averages = 12 #Counts
wait = .6*num_averages #seconds (.6*num_averages? [for IF=3e3])
#trform = 'PLOG'
trform = 'PHAS'
h5py_filepath = 'C:\\Qtlab\\'
now = dt.datetime.now()
date_time = '{month}_{day}_{year}_{hour}(1)'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour)
h5py_filename = 'test'# + date_time

fp = h5py.File(h5py_filepath + h5py_filename, 'w')
# Get Instruments
VNA = qt.instruments.get('VNA')
YOKO = qt.instruments.get('YOKO')

# Get original parameters VNA
init_fstart = VNA.get_fstart()
init_fstop = VNA.get_fstop()
init_ifbw = VNA.get_ifbw()
init_trform = VNA.get_trform()
init_num_averages = VNA.get_avgnum()

# Get original parameters YOKO
old_ramp_time = YOKO.get_slope_interval()

# Set parameters VNA
VNA.set_fstart(start)
VNA.set_fstop(stop)
VNA.set_ifbw(IF)
VNA.set_trform(trform)

# Set parameters YOKO
ramp_time = YOKO.set_ramp_intervals(step = current_step, rate = ramp_rate)

# Populate current values
currents = []
if current_step>0:
    value = min_current
    while value < max_current:
        currents.append(value)
        value += current_step
    currents.append(value)
else:
    value = max_current
    while value > min_current:
        currents.append(value)
        value += current_step
    currents.append(value)
    
if (YOKO.get_output_level() != currents[0]):    
    time.sleep(YOKO.change_current(currents[0])) #set current to staritng value

i = 0
for current in currents:
    print ('Testing at %s Amps' %current)
    YOKO.change_current(current)
    time.sleep(ramp_time)    #wait for current to reach new value
    VNA.average(num_averages, wait)
    fdata = VNA.getfdata()
    trace_data = VNA.gettrace()
    fp.create_dataset('f_data{}'.format(i), data=fdata)
    fp.create_dataset('trace_data{}'.format(i), data=trace_data)
    i+=1
fp.create_dataset('current_data', data = currents)    
fp.close()

VNA.set_fstart(init_fstart)
VNA.set_fstop(init_fstop)
VNA.set_ifbw(init_ifbw)
VNA.set_trform(init_trform)
VNA.set_avgnum(init_num_averages)

YOKO.set_slope_interval(old_ramp_time) 