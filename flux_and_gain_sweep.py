# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 16:05:57 2016

@author: HATLAB
"""

# Settings --------------------------------------------------------------------
VNA_NAME = 'VNA'
CS_NAME = 'YOKO'
GEN_NAME = 'GEN'

MIN_POWER = -40 #dBm total power
MAX_POWER = -32 #dBm total power
MIN_POWER = MIN_POWER + 20 # factor in -20dB attenuator
MAX_POWER = MAX_POWER + 20 # factor in -20dB attenuator 
POWER_STEP = .2 #dbm
MIN_PUMP_FREQUENCY = 15.022871e9 #Hz
MAX_PUMP_FREQUENCY = 15.042871e9 #Hz
PUMP_FREQUENCY_STEP = .0025e9
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

MIN_CURRENT = 0.1e-3 #Ampere
MAX_CURRENT = .2e-3 #Ampere         1e-3  previous
CURRENT_STEP = .05e-3 #Ampere    .0025e-3 previous
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
init_fstart = VNA.get_fstart()
init_fstop = VNA.get_fstop()
init_ifbw = VNA.get_ifbw()
init_trform = VNA.get_trform()
init_num_averages = VNA.get_avgnum()
init_elec_delay = VNA.get_electrical_delay()
init_phase_offset = VNA.get_phase_offset()
#previous state GEN
init_frequency = GEN.get_frequency()
init_power = GEN.get_power()
#previous state YOKO
init_ramp_time = YOKO.get_slope_interval()

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
    global init_frequency
    init_frequency = GEN.get_frequency()
    global init_power
    init_power = GEN.get_power()
    global init_ramp_time
    init_ramp_time = YOKO.get_slope_interval()
        
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
    # Set parameters YOKO
    global ramp_time
    ramp_time = YOKO.set_ramp_intervals(step = CURRENT_STEP, rate = RAMP_RATE)
   
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
    
def set_currents(currents = None):
    '''
    Creates a list of currents to sweep through. (Note: if current_step is 
    negative it will count from max_current down to min_current)
    '''
    global CURRENTS
    if currents is None:
        CURRENTS = np.append(np.arange(MIN_CURRENT, 
                                       MAX_CURRENT, 
                                       abs(CURRENT_STEP),
                             MAX_CURRENT)
        if CURRENT_STEP < 0:
            CURRENTS[::-1]
    else:
        CURRENTS = currents
        
def get_normalization_data(index):
    '''
    Gets a data trace without the pump being on to use to normalize raw data
    '''
    GEN.set_output_status(0)
    VNA.average(num_averages, wait)
    global NORMALIZE_DATA
    NORMALIZE_DATA[index] = VNA.gettrace()
    GEN.set_output_status(1)
    
def get_measurement_bandwidth():
    global MEASURE_BANDWIDTH
    MEASURE_BANDWIDTH = VNA.getfdata()
    
def sweep_power():
    '''
    Runs the sweep over the powers and frequencies specified in the #Settings 
    or set via set_frequencies/ set_powers.  The data is saved to SWEEP_DATA in 
    the form [frequency_index][power_index][data]. The frequencies of the trace 
    are saved to MEASURED_FREQUENCIES  
    '''
#    global FREQUENCIES
#    global POWERS
#    global MEASURED_FREQUENCIES
    get_measurement_bandwidth()
    num_tests = len(FREQUENCIES)*len(POWERS)
    print('Number of tests = {}. Time per test = {} sec. Total time ~ {} min'
                                .format(num_tests, wait, num_tests*wait/60))
    global SWEEP_DATA
    SWEEP_DATA = np.empty((len(CURRENTS),
                           len(FREQUENCIES),
                           len(POWERS), 
                           2,   # added 2
                           len(MEASURE_BANDWIDTH)))
    global NORMALIZE_DATA
    NORMALIZE_DATA = np.empty((len(FREQUENCIES), 2, len(MEASURE_BANDWIDTH)))    
    if (YOKO.get_output_level() != CURRENTS[0]):    
        time.sleep(YOKO.change_current(CURRENTS[0]))
    for current_index in range(len(CURRENTS)):
        YOKO.change_current(CURRENTS[current_index])
        time.sleep(ramp_time)    #wait for current to reach new value
        for freq_index in range(len(FREQUENCIES)): 
            GEN.set_frequency(FREQUENCIES[freq_index])
            get_normalization_data(freq_index)
            for power_index in range(len(POWERS)):
                GEN.set_power(POWERS[power_index])
                print ('Power = {}dBm, Frequency = {}GHz, #{}/{}'
                                .format(POWERS[power_index]-20, 
                                        FREQUENCIES[freq_index]/1e9, 
                                        power_index+freq_index*len(POWERS)+1, 
                                        num_tests))
                VNA.average(num_averages, wait)
                trace_data = VNA.gettrace()
                SWEEP_DATA[current_index, freq_index, power_index] = trace_data 
    GEN.set_power(-20)
    
    
    
    
    
    
    
    