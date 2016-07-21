# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 10:47:57 2016

@author: HATLAB
"""

import qt
import time
import datetime as dt
import numpy as np
import h5py
from hatlab import linearfit as fit

# Settings --------------------------------------------------------------------

VNA_NAME = 'VNA'
GEN_NAME = 'GEN'
CS_NAME = 'YOKO'

MIN_POWER_LOW = -80 #dBm total power
MAX_POWER_LOW = -50 #dBm total power
POWER_STEP_LOW = .1 #dbm
MIN_POWER_MID = MAX_POWER_LOW
MAX_POWER_MID = -20 #dBm
POWER_STEP_MID = 1 #dBm
MIN_POWER_HIGH = MAX_POWER_MID
MAX_POWER_HIGH = 5 #dBm
POWER_STEP_HIGH = 2

#MIN_PUMP_FREQUENCY = 15.0300871e9 #Hz
#MAX_PUMP_FREQUENCY = 15.0340871e9 #Hz
#PUMP_FREQUENCY_STEP = .002e9
PUMP_FREQUENCY = 15.0320871e9 #Hz
PUMP_POWER = -32 #dBm
PUMP_POWER = PUMP_POWER + 20 #to factor in attenuator

MIN_MEASURE_FREQUENCY = 8.7919e9 #Hz
MAX_MEASURE_FREQUENCY = 8.8919e9 #Hz
FREQUENCY_STEP = 1e9 #Hz

START = MIN_MEASURE_FREQUENCY #Hz
STOP = MAX_MEASURE_FREQUENCY #Hz
IF = 3e3 #Hz
NUM_AVERAGES = 24 #Counts
WAIT = .6*NUM_AVERAGES #seconds (.6*num_averages? [for IF=3e3])
TRFORM = 'PLOG' #'MLOG'
ELECTRICAL_DELAY = 63e-9 #sec
TRIGGER_SOURCE = 'BUS'
AVG_TRIGGER = 1

#MIN_CURRENT = 0.239e-3 #Ampere
#MAX_CURRENT = 0.24e-3 #Ampere         1e-3  previous
#CURRENT_STEP = .001e-3 #Ampere    .0025e-3 previous
CURRENT = .24e-3  #Ampere
RAMP_RATE = .01 #Ampere/second
YOKO_PROGRAM_FILE_NAME = 'fluxsweep.csv'

PHASE_OFFSET = 180

# End of Settings -------------------------------------------------------------
VNA = None
GEN = None
YOKO = None
def get_instruments():
    global VNA
    VNA = qt.instruments.get(VNA_NAME)
    global GEN
    GEN = qt.instruments.get(GEN_NAME)
    global YOKO
    YOKO = qt.instruments.get(CS_NAME)
# Previous state VNA
init_fstart = None
init_fstop = None
init_ifbw = None
init_trform = None
init_num_averages = None
init_elec_delay = None
init_phase_offset = None
init_trigger_source = None
init_avg_trigger = None
#previous state GEN
init_frequency = None
init_power = None
#previous state YOKO
init_ramp_time = None

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
    global init_phase_offset
    init_phase_offset = VNA.get_phase_offset()
    global init_trigger_source
    init_trigger_source = VNA.get_trigger_source()
    global init_avg_trigger
    init_avg_trigger = VNA.get_avg_trigger()
    global init_frequency
    init_frequency = GEN.get_frequency()
    global init_power
    init_power = GEN.get_power()
    global init_ramp_time
    init_ramp_time = YOKO.get_slope_interval()
    
RAMP_TIME = None        
def set_instrument_parameters():
    '''
    Sets the instruments to the #Settings values for the test to be run
    '''
    # set VNA parameters
    VNA.set_fstart(START)
    VNA.set_fstop(STOP)
    VNA.set_ifbw(IF)
    VNA.set_trform(TRFORM)
    VNA.set_electrical_delay(ELECTRICAL_DELAY)    
    VNA.set_phase_offset(PHASE_OFFSET)
    VNA.set_trigger_source(TRIGGER_SOURCE)
    VNA.set_avg_trigger(AVG_TRIGGER)
    # Set parameters YOKO
#    global RAMP_TIME
#    RAMP_TIME = YOKO.set_ramp_intervals(step = CURRENT_STEP, rate = RAMP_RATE)

MEASURE_BANDWIDTH = None    
def get_measurement_bandwidth():
    global MEASURE_BANDWIDTH
    MEASURE_BANDWIDTH = VNA.getfdata()
    
POWERS = None
def set_powers(powers = None):
    '''
    Populates a list of powers to be run through
    '''
    global POWERS
    if powers is None:
        power_low = np.arange(MIN_POWER_LOW, MAX_POWER_LOW, POWER_STEP_LOW)
        power_mid = np.append(power_low,
                              np.arange(MIN_POWER_MID, MAX_POWER_MID, POWER_STEP_MID))
        power_high = np.append(power_mid, 
                               np.arange(MIN_POWER_HIGH, MAX_POWER_HIGH, POWER_STEP_HIGH))
        POWERS = np.append(power_high, MAX_POWER_HIGH)
    else:
        POWERS = powers

MAXIMUMS = None
SWEEP_DATA = None        
def sweep():
    global MAXIMUMS
    MAXIMUMS = np.empty(len(POWERS))
    global SWEEP_DATA
    SWEEP_DATA = np.empty(len(POWERS), 2, len(MEASURE_BANDWIDTH))
    GEN.set_frequency(PUMP_FREQUENCY)
    GEN.set_power(PUMP_POWER)
    GEN.set_output_status(1)
    if (YOKO.get_output_level() != CURRENT): 
        # Change current to starting currents
        time.sleep(YOKO.change_current(CURRENT))
    for i in range(len(POWERS)):
        VNA.set_power(POWERS[i])
        VNA.average(NUM_AVERAGES)
        trace = VNA.gettrace()
        SWEEP_DATA[i] = trace
        maximum = np.amax(fit.fit_data(trace[0], MEASURE_BANDWIDTH))
        MAXIMUMS[i] = maximum

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
    VNA.set_avgnum(init_num_averages)
    VNA.set_phase_offset(init_phase_offset)
    VNA.set_trigger_source(init_trigger_source)
    VNA.set_avg_trigger(init_avg_trigger)
    GEN.set_frequency(init_frequency)
    GEN.set_power(init_power)
    YOKO.set_slope_interval(init_ramp_time) 

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
        date_time = '{month}_{day}_{year}_{hour}_{minute}'.format(month = now.month,
                                                        day = now.day,
                                                        year = now.year,
                                                        hour = now.hour,
                                                        minute = now.minute)
        h5py_filename = 'dr_sweep_' + date_time
        filename = h5py_filepath + h5py_filename
    else:
        filename = h5py_filepath + filename
    outfile = h5py.File(filename, 'w')
    print "Saving data to %s" %filename
    outfile.create_dataset('measure_frequencies', data = MEASURE_BANDWIDTH)
    outfile.create_dataset('powers', data = POWERS) 
    outfile.create_dataset('maximums', data = MAXIMUMS)
    outfile.create_dataset('sweep_data', data = SWEEP_DATA)       
    outfile.close()
    
def run_sweep(filename = None, save_data = True):
    '''
    Command to initial instruments, set parameters, run sweep, save data, etc.
    This uses settings in #Settings or the most recent changes made by the set_
    methods
    '''
    get_instruments()
    store_instrument_parameters()
    set_instrument_parameters()
    set_powers()
    #get_normalization_data()
    sweep()
    reset_instrument_state()
    if save_data:
        save_data_to_h5py(filename)    
    
if __name__ == '__main__':
    run_sweep()        
def test_power_sweep():
    power = -80.0    
    while power < 10:
        VNA.set_power(power)
        print('VNA power = {}. Code power = {}'.format(VNA.get_power(), power))
        print("Attenuation = %s" % VNA.receive(':SOUR:POW:ATT?'))
        power += 1
        time.sleep(.5)