# -*- coding: utf-8 -*-
"""
Created on Fri Jul 08 11:52:42 2016

@author: Erick
"""
import numpy as np
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

print powers
npp = np.arange(MIN_POWER, MAX_POWER, POWER_STEP)
npp = np.append(npp, MAX_POWER)
print npp
print''
print frequencies
print np.arange(MIN_PUMP_FREQUENCY, MAX_PUMP_FREQUENCY, PUMP_FREQUENCY_STEP).append(MAX_FREQUENCY)