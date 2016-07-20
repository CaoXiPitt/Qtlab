# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 16:14:27 2016

@author: HatLabUnderGrad2
"""

path = 'C:\\Qtlab\\gain_sweep_data\\'




import matplotlib.pyplot as plt
import numpy as np
import h5py
import numpy.ma as ma
from numpy import log10, pi, sqrt
from lmfit.models import LorentzianModel
from lmfit import Model
from matplotlib.widgets import Slider
plt.ioff()

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
    
#load h5py file and data sets
fp = h5py.File(path+'fg_sweep_7_18_2016_18_1', 'r')

pumpFreqs = fp['pump_frequencies'][:]*10**-9
pumpPowers = fp['pump_powers'][:]-20
sigFreq = fp['measure_frequencies'][:]*10**-9
normals = fp['normal_data'][:]
sweep_data= fp['sweep_data'][:] 

#These will become the dimension lengths of the graph data arrays.
pumpFreqNum=len(pumpFreqs)
pumpPowerNum=len(pumpPowers)

#Create the Model for the gain function. See lmfit documentation for details.
GainModel = Model(Gain)

GainModel.set_param_hint('Go', value=10, min=0, vary=True)
GainModel.set_param_hint('La', value=.01, min=0, vary=True)
GainModel.set_param_hint('Lb', value=.01, min=0, vary=True)
GainModel.set_param_hint('center', value=8, min=7, max=9, vary=True)

#Create the arrays that will graph the data.
fittedData= np.zeros([pumpFreqNum, pumpPowerNum, len(sigFreq)]) #Will hold the "best values" from the Gain fits
fittedData1= np.zeros([pumpFreqNum, pumpPowerNum, len(sigFreq)]) #Will hold the "best values" from Lorentzian fits
dataSet=np.zeros([pumpFreqNum,pumpPowerNum,8]) #will hold the fit parameters given by each Gain fit
paramData=np.zeros([pumpFreqNum,pumpPowerNum,8]) #will hold the fit parameters given by each Lorentzian fit
normalData=np.zeros([pumpFreqNum, pumpPowerNum, len(sigFreq)]) #will hold the raw data after it has been normalized

for testNumF in range(pumpFreqNum):

    
    pumpFrequency = pumpFreqs[testNumF] 
    
    normal = normals[testNumF,0]
    
    print pumpFrequency
    
    for testNumP in range(pumpPowerNum):
        
        pumpPower = pumpPowers[testNumP]
        
        #normalize the individual data set
        gainRaw = sweep_data[testNumF,testNumP,0,:]-normal
        
        #convert data to Nat units. cannot be in dB when it is fit.
        gainNat = dB_ConvertFrom(gainRaw)
        gainDB= dB_ConvertTo(gainNat)
        
        maximum=gainNat.max()        
        centerIndex = gainNat.argmax()
        dim1 = int(centerIndex/1601)
        dim2 = centerIndex%1601        
        centerish = sigFreq[dim1,dim2]
#        centerish = sigFreq[centerIndex]
         
        ######################################################################
        
         #Fit and graph the data using both Lorentzian and Gain Models, then save fit data.
        
        gain = gainNat[0]
        freqs = sigFreq[0]
        print 'gain : {}, freqs : {}'.format(gain.shape, freqs.shape)

        guess = LorentzianModel().guess(gain-1, x=freqs)
        result = LorentzianModel().fit(gain-1, guess, x=freqs)
        
        sigma = result.best_values['sigma']
        amp = result.best_values['amplitude']
        center1 = result.best_values['center']
        BW1 = 2*sigma
        Gmax1  = amp/(pi*sigma) +1 
        chi1 = result.chisqr
        
        paramData[testNumF,testNumP,0]=pumpFrequency
        paramData[testNumF,testNumP,1]=pumpPower
        paramData[testNumF,testNumP,2]=Gmax1
        paramData[testNumF,testNumP,3]=center1
        paramData[testNumF,testNumP,4]=BW1
        paramData[testNumF,testNumP,5]=chi1
    
        fig=plt.figure()
        fig.suptitle('Gain by Frequency'+'(Pp='+ str(pumpPower) +'Fp='+str(pumpFrequency)+')', fontsize=20)
        plt.xlabel('Signal Frequency (GHz)', fontsize=10)
        plt.ylabel('Gain (dB)', fontsize=10)
        plt.plot(freqs, gainDB[0], 'r.', markeredgewidth=.3)
        plt.plot(freqs, dB_ConvertTo(result.best_fit+1), 'b-')
        fig.savefig(path+'Graphs\\Lorentzian Curves\\Pp='+ str(pumpPower) +'Fp='+str(pumpFrequency)+'.pdf')
        plt.close(fig)
        
        if BW1<.001:
            guess = LorentzianModel().guess(gain-1, x=freqs, amplitude=0)
            result = LorentzianModel().fit(gain-1, guess, x=freqs, amplitude=0)
            
            sigma = result.best_values['sigma']
            amp = result.best_values['amplitude']
            center1 = result.best_values['center']
            BW1 = 2*sigma
            Gmax1  = amp/(pi*sigma) +1 
            chi1 = result.chisqr
            
            paramData[testNumF,testNumP,0]=pumpFrequency
            paramData[testNumF,testNumP,1]=pumpPower
            paramData[testNumF,testNumP,2]=Gmax1
            paramData[testNumF,testNumP,3]=center1
            paramData[testNumF,testNumP,4]=BW1
            paramData[testNumF,testNumP,5]=chi1
        
            fig=plt.figure()
            fig.suptitle('Gain by Frequency'+'(Pp='+ str(pumpPower) +'Fp='+str(pumpFrequency)+')', fontsize=20)
            plt.xlabel('Signal Frequency (GHz)', fontsize=10)
            plt.ylabel('Gain (dB)', fontsize=10)
            plt.plot(freqs, gainDB, 'r.', markeredgewidth=.3)
            plt.plot(freqs, dB_ConvertTo(result.best_fit+1), 'b-')
            fig.savefig(path+'Graphs\\Lorentzian Curves\\Pp='+ str(pumpPower) +'Fp='+str(pumpFrequency)+'.pdf')
            plt.close(fig)
            
        #fittedData1[testNumF,testNumP] = dB_ConvertTo(result.best_fit+1)
        #normalData[testNumF,testNumP] = gainRaw
        
        
        ################################################################# 
        
        GainModel.set_param_hint('center', value=center1, min=8.8, max=8.9, vary=True)        
        GainModel.set_param_hint('Go', value=Gmax1, min=Gmax1*.8, max = Gmax1*1.2, vary=True)
        
        
#        if testNumF>0 and testNumP>0:
#            GainModel.set_param_hint('La', value=dataSet[testNumF,testNumP-1][5], min=0, vary=True)
#            GainModel.set_param_hint('Lb', value=dataSet[testNumF,testNumP-1][6], min=0, vary=True)
#        if (testNumF>0) and testNumP==0:
#            GainModel.set_param_hint('La', value=dataSet[testNumF-1,testNumP][5], min=0, vary=True)
#            GainModel.set_param_hint('Lb', value=dataSet[testNumF-1,testNumP][6], min=0, vary=True)

        results = GainModel.fit(gainNat, x=sigFreq)
        
        #Function for getting parameters
        def param(i):
            return results.best_values[i]
        
        maxGain = param('Go')            
        La = param('La')
        Lb = param('Lb')
        center = param('center')
        
        fwhm = 2*La*Lb*sqrt(maxGain)/(La+Lb)
        chi = results.redchi        
        
        
        fig=plt.figure()
        fig.suptitle('Gain by Frequency'+'(Pp='+ str(pumpPower) +'Fp='+str(pumpFrequency)+')', fontsize=20)
        plt.xlabel('Signal Frequency (GHz)', fontsize=10)
        plt.ylabel('Gain (dB)', fontsize=10)
        plt.plot(sigFreq, gainDB, 'r.', markeredgewidth=.3)
        plt.plot(sigFreq, dB_ConvertTo(results.best_fit), 'b-')
        fig.savefig(path+'Graphs\\Special Curves\\Pp='+ str(pumpPower) +'Fp='+str(pumpFrequency)+'.pdf')
        plt.close(fig)        
        
    
        dataSet[testNumF,testNumP][0]=pumpFrequency
        dataSet[testNumF,testNumP][1]=pumpPower
        dataSet[testNumF,testNumP][2]=maxGain
        dataSet[testNumF,testNumP][3]=fwhm
        dataSet[testNumF,testNumP][4]=center
        dataSet[testNumF,testNumP][5]=La
        dataSet[testNumF,testNumP][6]=Lb
        dataSet[testNumF,testNumP][7]=chi
        
        
        fittedData[testNumF,testNumP] = dB_ConvertTo(results.best_fit)



#Graph all the color plots
       
X = dataSet[:,:,0]
Y = dataSet[:,:,1]
gainAll = dataSet[:,:,2]
fig1=plt.figure(1)
fig1.suptitle('Max Gain (dB) by Pp and Fp', fontsize=20)
plt.axis([X.min(), X.max(), Y.min(), Y.max()])
plt.xlabel('Pump Frequency (GHz)', fontsize=10)
plt.ylabel('Pump Power (dBm)', fontsize=10)
plt.pcolor(X, Y, dB_ConvertTo(gainAll), cmap='brg')
plt.colorbar()
fig1.savefig(path+'Graphs\\Max Gain by Pp and Fp ALL Spec.pdf')
plt.close(fig1)

fig1=plt.figure(1)
fig1.suptitle('Log10 of Chi Square ', fontsize=20)
plt.axis([X.min(), X.max(), Y.min(), Y.max()])
plt.xlabel('Pump Frequency (GHz)', fontsize=10)
plt.ylabel('Pump Power (dBm)', fontsize=10)
plt.pcolor(X, Y, log10(dataSet[:,:,7]), cmap='brg')
plt.colorbar()
fig1.savefig(path+'Graphs\\Chi Square All Spec.pdf')
plt.close(fig1)

#######################################
X=paramData[:,:,0]
Y=paramData[:,:,1]
#Gain=dB_ConvertTo(ma.masked_equal(paramData[:,:,2], 0))
Gains=ma.masked_less(paramData[:,:,2], 0)
Chi=paramData[:,:,5]
Center = paramData[:,:,3]
GainDB = dB_ConvertTo(paramData[:,:,2])
Gain20 = ma.masked_where(GainDB>21, GainDB, copy=True)
Gain20 = ma.masked_where(Gain20<20, Gain20, copy=True)
fig1=plt.figure(1)
fig1.suptitle('Max Gain (dB) by Pp and Fp', fontsize=20)
plt.axis([X.min(), X.max(), Y.min(), Y.max()])
plt.xlabel('Pump Frequency (GHz)', fontsize=10)
plt.ylabel('Pump Power (dBm)', fontsize=10)
plt.pcolor(X, Y, Gains, cmap='brg')
plt.colorbar()
fig1.savefig(path+'Graphs\\Max Gain ALL Lorentz.pdf')
plt.close(fig1)

fig1=plt.figure(1)
fig1.suptitle('Center Freq (GHz) by Pp and Fp', fontsize=20)
plt.axis([X.min(), X.max(), Y.min(), Y.max()])
plt.xlabel('Pump Frequency (GHz)', fontsize=10)
plt.ylabel('Pump Power (dBm)', fontsize=10)
plt.pcolor(X, Y, Center , cmap='brg')
plt.colorbar()
fig1.savefig(path+'Graphs\\Center Lorentz.pdf')
plt.close(fig1)

fig1=plt.figure(1)
fig1.suptitle('Max Gain by Pp and Fp', fontsize=20)
plt.axis([X.min(), X.max(), Y.min(), Y.max()])
plt.xlabel('Pump Frequency (GHz)', fontsize=10)
plt.ylabel('Pump Power (dBm)', fontsize=10)
plt.pcolor(X, Y, Gain20, cmap='brg')
plt.colorbar()
fig1.savefig(path+'Graphs\\Max Gain 20.pdf')
plt.close(fig1)

fig2=plt.figure(2)
fig2.suptitle('Chi by Pp and Fp', fontsize=20)
plt.axis([X.min(), X.max(), Y.min(), Y.max()])
plt.xlabel('Pump Frequency (GHz)', fontsize=10)
plt.ylabel('Pump Power (dBm)', fontsize=10)
plt.pcolor(X, Y, Chi, cmap='brg')
plt.colorbar()
fig2.savefig(path+'Graphs\\Chi Square All Lorentz.pdf')
plt.close(fig2)


################################


sweep_freqs = pumpFreqs.tolist()
sweep_powers = pumpPowers.tolist()
for i in range(len(sweep_powers)):  # Remove floating point error
    sweep_powers[i] = int(sweep_powers[i]*10)/10.0


measurement_frequency = sigFreq



# Main Data Plot Setup
data_plot, = plt.plot(measurement_frequency, normalData[0,10], 'ro', markersize=3, markeredgewidth=.01)
fit_plot, = plt.plot(measurement_frequency, fittedData[0,10], 'b-')

plt.axis([measurement_frequency[0], measurement_frequency[-1], -5, 30])
plt.gcf().subplots_adjust(left = .05, right = .95,top = .95, bottom = .15)
plt.title('Power and Frequency Sweep')
plt.xlabel('Frequency (Ghz)')
plt.ylabel('Gain (dB)')

# Slider Setup
freq_axes = plt.axes([0.2, 0.01, 0.65, 0.03])
freq_slider = Slider(freq_axes, 'Frequency', min(sweep_freqs), max(sweep_freqs), valinit=min(sweep_freqs), valfmt = '%.4f GHz')
power_axes = plt.axes([0.2, 0.05, 0.65, 0.03])
power_slider = Slider(power_axes, 'Power', min(sweep_powers), max(sweep_powers), valinit=min(sweep_powers), valfmt = '%.1f dB')

def update(val):
    sval = int(power_slider.val*10)/10.0
    fval = freq_slider.val
    findex = sweep_freqs.index(min(sweep_freqs, key=lambda x:abs(x-fval)))
    pindex = sweep_powers.index(min(sweep_powers, key=lambda x:abs(x-sval)))
    data_plot.set_ydata(normalData[findex, pindex])
    fit_plot.set_ydata(fittedData1[findex,pindex])
    if (power_slider.val != sweep_powers[pindex]):
        power_slider.set_val(sweep_powers[pindex])
    if (freq_slider.val != sweep_freqs[findex]):
        freq_slider.set_val(sweep_freqs[findex])
        
power_slider.on_changed(update)
freq_slider.on_changed(update)
plt.show()




fp.close()












