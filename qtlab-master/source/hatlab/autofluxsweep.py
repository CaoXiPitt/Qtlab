# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 18:14:22 2016

@author: HatLabUnderGrads
"""

import qt 
from hatlab import fluxsweep
import h5py
import numpy as np
import time
import datetime as dt
import h5py
import sys
import fluxplot
import numpy as np

# Settings --------------------------------------------------------------------
VNA_NAME = 'VNA'
CS_NAME = 'YOKO'
SWITCH_NAME = 'SWT'

MIN_CURRENT = 0.1e-3 #Ampere
MAX_CURRENT = .25e-3 #Ampere         1e-3  previous
CURRENT_STEP = .05e-3 #Ampere    .0025e-3 previous
RAMP_RATE = .01 #Ampere/second
YOKO_PROGRAM_FILE_NAME = 'fluxsweep.csv'

SIGNAL_START = 8.8e9 #Hz
SIGNAL_STOP =9.2e9 #Hz
IF = 3e3 #Hz
IDLE_START = 4.5e9 #Hz
IDLE_STOP = 5.0e9 #Hz

NUM_AVERAGES = 12 #Counts
trform = 'PLOG'
PHASE_OFFSET = -180
TRIGGER_SOURCE = 'bus'
AVG_TRIGGER = 1

def create_currents():
    return np.append(np.arange(MIN_CURRENT, 
                                       MAX_CURRENT, 
                                       abs(CURRENT_STEP)),
                             MAX_CURRENT)

def run_sweep():
    SWT = qt.instruments.get(SWITCH_NAME)
    SWT.set_mode('S_ss')
    fluxsweep.run_sweep(sweep_currents = create_currents(),
                       filename = 'C:\\Qtlab\\flux_sweep_data\\signal_test',
                       measure_bandwidth = [SIGNAL_START, SIGNAL_STOP])
    SWT.set_mode('S_ii')
    fluxsweep.run_sweep(sweep_currents = create_currents(),
                        filename = 'C:\\Qtlab\\flux_sweep_data\\idle_test',
                        measure_bandwidth = [IDLE_START, IDLE_STOP])

if __name__ == '__main__':
    run_sweep()
    
def save_data_to_h5py(filename = None):
    string = ''
    i = 0
    name = 'first'
    running  = True
    while running:
        try:
            outfile = h5py.File(r'E:\ErickTest\%s'%(name + string), 'w-')
            running = False
        except IOError:
            i+=1
            string = str(i)
    outfile.close()

