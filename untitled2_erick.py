# -*- coding: utf-8 -*-
"""
Created on Fri Jul 08 11:52:42 2016

@author: Erick
"""
import numpy as np
a = np.zeros((3,3,2,5))
b = np.array([[1,2,3],[4,5,6]])
a[2,2] = [[1,2,3,4,5], [5,4,3,2,1]]
print a
print b
print b