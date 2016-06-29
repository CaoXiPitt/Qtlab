# -*- coding: utf-8 -*-
"""
A script file to do flux sweeps

@author: Hatlab : Erick Brindock
"""
import qt
import time

from instrument import Instrument 
from instruments import Instruments
# Settings
vna_name = 'VNA'
cs_name = 'YOKO'
min_current = 0 #Ampere
max_current = 10e-3 #Ampere
current_step = 1e-3 #Ampere
ramp_rate = .01 #Ampere/second
yoko_program_file_name = 'fluxsweep.csv'
start = 7e9 #Hz
stop = 8e9 #Hz
IF = 3e3 #Hz
num_averages = 12 #Counts
wait = 7.2 #seconds (.6*num_averages? [for IF=3e3])

# Get Instruments
VNA = qt.instruments.get('VNA')
YOKO = qt.instruments.get('YOKO')
ramp_time = YOKO.set_ramp_intervals(step = current_step, rate = ramp_rate)
num_steps = YOKO.create_program(filename = yoko_program_file_name,
                    step = current_step,
                    min_current = min_current,
                    max_current = max_current)
VNA.set_fstart(start)
VNA.set_fstop(stop)
VNA.set_ifbw(IF)
VNA.
print num_steps
for i in range(num_steps+1):
    YOKO.step_current()
    time.sleep(ramp_time)
    
