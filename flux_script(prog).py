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
max_current = 1e-3 #Ampere
current_step = .0025e-3 #Ampere
ramp_rate = .01 #Ampere/second
yoko_program_file_name = 'fluxsweep.csv'
start = 5e9 #Hz
stop =6.5e9 #Hz
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
h5py_filename = 'flux_data_' + date_time

fp = h5py.File(h5py_filepath + h5py_filename, 'w')
# Get Instruments
VNA = qt.instruments.get('VNA')
YOKO = qt.instruments.get('YOKO')

init_fstart = VNA.get_fstart()
init_fstop = VNA.get_fstop()
init_ifbw = VNA.get_ifbw()
init_trform = VNA.get_trform()
init_num_averages = VNA.get_avgnum()

#YOKO.set_output(1)

old_ramp_time = YOKO.get_slope_interval()
ramp_time = YOKO.set_ramp_intervals(step = current_step, rate = ramp_rate)
num_steps = YOKO.create_program(filename = yoko_program_file_name,
                    step = current_step,
                    min_current = min_current,
                    max_current = max_current)

VNA.set_fstart(start)
VNA.set_fstop(stop)
VNA.set_ifbw(IF)
VNA.set_trform(trform)

currents = []

for i in range(num_steps):
    YOKO.step_current()
    time.sleep(ramp_time)
    VNA.average(num_averages, wait)
    fdata = VNA.getfdata()
    trace_data = VNA.gettrace()
    currents.append(YOKO.get_output_level())
    fp.create_dataset('f_data{}'.format(i), data=fdata)
    fp.create_dataset('trace_data{}'.format(i), data=trace_data)

fp.create_dataset('current_data', data = currents)
fp.attrs['total_sweeps'] = len(currents)    
fp.close()

VNA.set_fstart(init_fstart)
VNA.set_fstop(init_fstop)
VNA.set_ifbw(init_ifbw)
VNA.set_trform(init_trform)
VNA.set_avgnum(init_num_averages)

YOKO.set_slope_interval(old_ramp_time)
#YOKO.set_output(0) 