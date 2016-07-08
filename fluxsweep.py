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

# Settings
VNA_NAME = 'VNA'
CS_NAME = 'YOKO'
MIN_CURRENT = 0 #Ampere
MAX_CURRENT = .5e-3 #Ampere         1e-3  previous
CURRENT_STEP = .025e-3 #Ampere    .0025e-3 previous
RAMP_RATE = .01 #Ampere/second
yoko_program_file_name = 'fluxsweep.csv'
start = 7.6e9 #Hz
stop =9.2e9 #Hz
IF = 3e3 #Hz
num_averages = 12 #Counts
wait = .6*num_averages #seconds (.6*num_averages? [for IF=3e3])
#trform = 'PLOG'
trform = 'PHAS'
h5py_filepath = 'C:\\Qtlab\\flux_sweep_data\\'
now = dt.datetime.now()
date_time = '{month}_{day}_{year}_{hour}_{minute}'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour,
                                                        minute = now.minute)
h5py_filename = 'signal_sweep_' + date_time

fp = h5py.File(h5py_filepath + h5py_filename, 'w')
# Get Instruments
VNA = qt.instruments.get('VNA')
YOKO = qt.instruments.get('YOKO')

#TODO -------------------------------------------------------------------------
#TODO  use global variables
#TODO  see untitled 2 and 4 for reference
#TODO -------------------------------------------------------------------------

def get_instruments(self,vna_name = VNA_NAME, cs_name = CS_NAME):
    self.VNA = qt.instruments.get(vna_name)
    self.YOKO = qt.instrments.get(cs_name)
    
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

ramp_time = 30
def set_instrument_parameters(self):
    VNA.set_fstart(start)
    VNA.set_fstop(stop)
    VNA.set_ifbw(IF)
    VNA.set_trform(trform)
    # Set parameters YOKO
    self.ramp_time = YOKO.set_ramp_intervals(step = CURRENT_STEP, rate = RAMP_RATE)

currents = []
# Populate current values
def create_currents(min_current = MIN_CURRENT,
                    max_current = MAX_CURRENT,
                    current_step = CURRENT_STEP):
    '''
    Creates a list of currents to sweep through. (Note: if current_step is 
    negative it will count from max_current down to min_current)
    '''
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

def store_instrument_parameters(self):
    self.init_fstart = VNA.get_fstart()
    self.init_fstop = VNA.get_fstop()
    self.init_ifbw = VNA.get_ifbw()
    self.init_trform = VNA.get_trform()
    self.init_num_averages = VNA.get_avgnum()
    self.old_ramp_time = YOKO.get_slope_interval()
    
frequency_data = []
def ask_frequency_data(self):
    self.frequency_data = VNA.getfdata()
    
phase_data = [] 
def sweep_current(self,currents):    
    if (YOKO.get_output_level() != currents[0]):    
        time.sleep(YOKO.change_current(currents[0])) #set current to staritng value
    i = 0
    for current in currents:
        print ('Testing at %s Amps' %current)
        YOKO.change_current(current)
        time.sleep(ramp_time)    #wait for current to reach new value
        VNA.average(num_averages, wait)
        fdata = VNA.getfdata()
        self.phase_data[i] = VNA.gettrace()[0]
        fp.create_dataset('trace_data{}'.format(i), data=phase_data)
        i+=1
    fp.create_dataset('frequency_data', data=fdata)
    fp.create_dataset('current_data', data = currents)    
    fp.close()

VNA.set_fstart(init_fstart)
VNA.set_fstop(init_fstop)
VNA.set_ifbw(init_ifbw)
VNA.set_trform(init_trform)
VNA.set_avgnum(init_num_averages)

YOKO.set_slope_interval(old_ramp_time)

if __name__ == '__main__':
    get_instruments()
    currents = create_currents()