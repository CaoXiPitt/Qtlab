# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 16:05:57 2016

A module containing the necessary information and methods to run a sweep over 
currents, frequencies, and powers.  It can be run as a stand alone module (ie.
execfile(%PATH%\flux_and_gain_sweep.py) in Qtlab), using the settings under the 
# Settings heading.  It can also be imported so certain parameters can be 
changed and the test can be run and rerun. The parameters which can be changed 
are the filename, and the currents, frequencies, and/or powers swept through.
   
@author: HATLAB  Erick Brindock
"""
import qt
import time
import datetime as dt
import h5py
import numpy as np
import fluxsweep

# Settings --------------------------------------------------------------------
VNA_NAME = 'VNA'
CS_NAME = 'YOKO'
GEN_NAME = 'GEN'

MIN_POWER = -40 #dBm total power
MAX_POWER = -32 #dBm total power
MIN_POWER = MIN_POWER + 20 # factor in -20dB attenuator
MAX_POWER = MAX_POWER + 20 # factor in -20dB attenuator 
POWER_STEP = 4 #dbm
MIN_PUMP_FREQUENCY = 15.0300871e9 #Hz
MAX_PUMP_FREQUENCY = 15.0340871e9 #Hz
PUMP_FREQUENCY_STEP = .002e9
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

MIN_CURRENT = 0.239e-3 #Ampere
MAX_CURRENT = 0.24e-3 #Ampere         1e-3  previous
CURRENT_STEP = .001e-3 #Ampere    .0025e-3 previous
RAMP_RATE = .01 #Ampere/second
YOKO_PROGRAM_FILE_NAME = 'fluxsweep.csv'

PHASE_OFFSET = 180
# End of Settings -------------------------------------------------------------
VNA = qt.instruments.get(VNA_NAME)
GEN = qt.instruments.get(GEN_NAME)
YOKO = qt.instruments.get(CS_NAME)

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
    global RAMP_TIME
    RAMP_TIME = YOKO.set_ramp_intervals(step = CURRENT_STEP, rate = RAMP_RATE)
    
POWERS = None   
def set_powers(powers = None):
    '''
    Populates a list of powers to be swept through
        Args:
            powers (numpy array) : powers to be swept through
    '''
    global POWERS
    if powers is None:
        POWERS = np.append(np.arange(MIN_POWER, MAX_POWER, POWER_STEP), 
                           MAX_POWER)
    else:
        POWERS = powers
FREQUENCIES = None    
def set_frequencies(frequencies = None):
    '''
    Populates a list of frequencies to be swept through
        Args:
            frequencies (numpy array) : frequencies to be swept through
    '''
    global FREQUENCIES
    if frequencies is None:
        FREQUENCIES = np.append(np.arange(MIN_PUMP_FREQUENCY, 
                                      MAX_PUMP_FREQUENCY, 
                                      PUMP_FREQUENCY_STEP), 
                            MAX_PUMP_FREQUENCY)
    else:
        FREQUENCIES = frequencies
        
CURRENTS = None    
def set_currents(currents = None):
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
        
NORMALIZE_DATA = None        
def get_normalization_data(index):
    '''
    Gets a data trace without the pump being on to use to normalize raw data
    '''
    GEN.set_output_status(0)
    VNA.average(NUM_AVERAGES)
    global NORMALIZE_DATA
    NORMALIZE_DATA[index] = VNA.gettrace()
    GEN.set_output_status(1)
    
MEASURE_BANDWIDTH = None    
def get_measurement_bandwidth():
    global MEASURE_BANDWIDTH
    MEASURE_BANDWIDTH = VNA.getfdata()
 
SWEEP_DATA = None    
def sweep():
    '''
    Runs the sweep over the powers and frequencies specified in the #Settings 
    or set via set_frequencies/ set_powers.  The data is saved to SWEEP_DATA in 
    the form [frequency_index][power_index][data]. The frequencies of the trace 
    are saved to MEASURED_FREQUENCIES  
    '''
#    global FREQUENCIES
#    global POWERS
#    global MEASURED_FREQUENCIES
    #get_measurement_bandwidth()
    global MEASURE_BANDWIDTH 
    MEASURE_BANDWIDTH = np.empty((len(CURRENTS), 1601))
    num_tests = len(FREQUENCIES)*len(POWERS)
    print('Number of tests = {}. Time per test = {} sec. Total time ~ {} min'
                                .format(num_tests, WAIT, num_tests*WAIT/60))
    global SWEEP_DATA
    SWEEP_DATA = np.empty((len(CURRENTS),
                           len(FREQUENCIES),
                           len(POWERS), 
                           2,   # added 2
                           len(MEASURE_BANDWIDTH[1])))
    global NORMALIZE_DATA
    NORMALIZE_DATA = np.empty((len(CURRENTS), 2, len(MEASURE_BANDWIDTH[1])))    
    if (YOKO.get_output_level() != CURRENTS[0]): 
        # Change current to starting currents
        time.sleep(YOKO.change_current(CURRENTS[0]))
    for current_index in range(len(CURRENTS)):
#        YOKO.change_current(CURRENTS[current_index])
#        time.sleep(RAMP_TIME)    #wait for current to reach new value
        print 'Performing fluxsweep'
        fluxsweep.run_sweep([CURRENTS[current_index]], save_data = False)
        mid_point = fluxsweep.get_resonant_frequency(CURRENTS[current_index])
        VNA.set_fcenter(mid_point)
        MEASURE_BANDWIDTH[current_index] = VNA.getfdata()
        print 'Getting Normalization Data'
        get_normalization_data(current_index)
        for freq_index in range(len(FREQUENCIES)): 
            GEN.set_frequency(FREQUENCIES[freq_index])
            for power_index in range(len(POWERS)):
                GEN.set_power(POWERS[power_index])
                print ('Power = {}dBm, Frequency = {}GHz, #{}/{}'
                                .format(POWERS[power_index]-20, 
                                        FREQUENCIES[freq_index]/1e9, 
                                        power_index+freq_index*len(POWERS)+1, 
                                        num_tests))
                #VNA.average(NUM_AVERAGES, WAIT)
                VNA.average(NUM_AVERAGES)
                trace_data = VNA.gettrace()
                SWEEP_DATA[current_index, freq_index, power_index] = trace_data 
    GEN.set_power(-20)
    
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
        h5py_filename = 'fg_sweep_' + date_time
        filename = h5py_filepath + h5py_filename
    else:
        filename = h5py_filepath + filename
    outfile = h5py.File(filename, 'w')
    print "Saving data to %s" %filename
    outfile.create_dataset('pump_frequencies', data = FREQUENCIES)
    outfile.create_dataset('pump_powers', data = POWERS)
    outfile.create_dataset('currents' , data = CURRENTS)
    outfile.create_dataset('normal_data', data = NORMALIZE_DATA)
    outfile.create_dataset('sweep_data', data = SWEEP_DATA)
    outfile.create_dataset('measure_frequencies', data = MEASURE_BANDWIDTH)        
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
    set_frequencies()
    set_currents()
    #get_normalization_data()
    sweep()
    reset_instrument_state()
    if save_data:
        save_data_to_h5py(filename)    
    
if __name__ == '__main__':
    run_sweep()    