# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 18:14:22 2016

@author: HatLabUnderGrads
"""

import qt 
from hatlab import fluxsweep
import h5py
import numpy as np

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