# -*- coding: utf-8 -*-
"""
Created on Wed Jul 06 11:13:39 2016

@author: HATLAB
"""

import h5py
#exists = True
#num = 0
#while exists:
#    try:    
#        fp = h5py.File('C:\\test\\test%s' %num, 'w-')
#    except IOError:
#        
#mdata = [1,2,3]
#fp.create_dataset('data', data = mdata)
#fp.close()
fp= h5py.File('C:\\Qtlab\\gain_sweep_data\\testing7_6_2016_13', 'r')

freqs = fp['frequencies'][:]
powers = fp['powers'][:]
print type(freqs)
print freqs
print type(powers)
print powers