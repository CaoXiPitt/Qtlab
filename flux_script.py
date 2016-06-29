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
min_current = 1e-3 #Ampere
max_current = 200e-3 #Ampere
current_step = 1e-3 #Ampere
ramp_rate = 1 #Ampere/second
yoko_program_file_name = 'fluxsweep.csv'


# Get Instruments
#VNA = I.get('VNA')
YOKO = qt.instruments.get('YOKO')
#
YOKO.create_program(filename = yoko_program_file_name,
                    step = current_step,
                    min_current = min_current,
                    max_current = max_current)
YOKO.test_program_function()
time.sleep(1)
YOKO.test_program_function()
