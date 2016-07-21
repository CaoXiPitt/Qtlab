# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 10:47:57 2016

@author: HATLAB
"""

import qt
import time
VNA = qt.instruments.get('VNA')
def test_power_sweep():
    power = -80.0    
    while power < 10:
        VNA.set_power(power)
        print('VNA power = {}. Code power = {}'.format(VNA.get_power(), power))
        print("Attenuation = %s" % VNA.receive(':SOUR:POW:ATT?'))
        power += 1
        time.sleep(.5)