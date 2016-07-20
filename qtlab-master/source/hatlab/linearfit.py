# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 10:09:56 2016

@author: HATLAB : Erick Brindock
"""

import matplotlib.pyplot as plt
import numpy as np
import h5py
import numpy.ma as ma
from numpy import log10, pi, sqrt
from lmfit.models import LorentzianModel
from lmfit import Model
from matplotlib.widgets import Slider

#Function for funding the indices of the max value in an array.
def findMax(i):
    
    return np.argwhere(i==i.max())
    
#Gain as a function of frequency (x), with parameters Go, center, La, Lb. Data will be fit to this function.
def Gain(x, Go, center, La, Lb):
    delta = (x-center)**2    
    top = 4*(-1+Go)*(La**2)*(Lb**2)
    bottom1 = -2*(-1+Go)*La*Lb*delta
    bottom2 = ((1+sqrt(Go))**2)*delta*(Lb**2+delta)
    bottom3 = (La**2)*((4*Lb**2)+(((1+sqrt(Go))**2)*delta))    
    return 1+(top/(bottom1+bottom2+bottom3))

def dB_ConvertFrom(x):
    return  10**(x/10)
    
def dB_ConvertTo(x):
    return 10*log10(x)

SWEEP_DATA  = None
def add_data_to_fit(data, normal = None):
    global SWEEP_DATA
    SWEEP_DATA = np.copy(data)
    if normal is not None:
        for i in range(SWEEP_DATA.shape[0]):
            SWEEP_DATA[i] = SWEEP_DATA[i]- normal[i]
MEASURE_FREQUENCY = None            
def add_frequency_data(frequencies):
    global MEASURE_FREQUENCY
    MEASURE_FREQUENCY = np.copy(frequencies)
    
#pumpFreqs = None
#pumpPowers = None    
##These will become the dimension lengths of the graph data arrays.
#pumpFreqNum=len(pumpFreqs)
#pumpPowerNum=len(pumpPowers)
#
#Create the Model for the gain function. See lmfit documentation for details.
GainModel = Model(Gain)

GainModel.set_param_hint('Go', value=10, min=0, vary=True)
GainModel.set_param_hint('La', value=.01, min=0, vary=True)
GainModel.set_param_hint('Lb', value=.01, min=0, vary=True)
GainModel.set_param_hint('center', value=8, min=7, max=9, vary=True)

gainNat = None

def main(gain_data):
    global gainNat
    gainNat = dB_ConvertFrom(gain_data)
    maximum=gainNat.max()        
    centerIndex = gainNat.argmax()
    return [maximum, centerIndex]   

def fit_data(gain_data, frequency_data):
    gain_natural = dB_ConvertFrom(gain_data)
    freqs = np.copy(frequency_data)
    #print 'gain : {}, freqs : {}'.format(gain_natural.shape, freqs.shape)

    guess = LorentzianModel().guess(gain_natural-1, x=freqs)
    result = LorentzianModel().fit(gain_natural-1, guess, x=freqs)
    
    sigma = result.best_values['sigma']
    amp = result.best_values['amplitude']
    center1 = result.best_values['center']
    BW1 = 2*sigma
    Gmax1  = amp/(pi*sigma) +1 
    chi1 = result.chisqr 
    if BW1<.001:
        guess = LorentzianModel().guess(gain_natural-1, x=freqs, amplitude=0)
        result = LorentzianModel().fit(gain_natural-1, guess, x=freqs, amplitude=0)
        
        sigma = result.best_values['sigma']
        amp = result.best_values['amplitude']
        center1 = result.best_values['center']
        BW1 = 2*sigma
        Gmax1  = amp/(pi*sigma) +1 
        chi1 = result.chisqr
#    fig=plt.figure()
#    #fig.suptitle('Gain by Frequency'+'(Pp='+ str(pumpPower) +'Fp='+str(pumpFrequency)+')', fontsize=20)
#    fig.suptitle('TestPlot')    
#    plt.xlabel('Signal Frequency (GHz)', fontsize=10)
#    plt.ylabel('Gain (dB)', fontsize=10)
#    plt.plot(freqs, dB_ConvertTo(gain_natural), 'r.', markeredgewidth=.3)
#    plt.plot(freqs, dB_ConvertTo(result.best_fit+1), 'b-')
#    plt.show()
    return dB_ConvertTo(result.best_fit+1)   
