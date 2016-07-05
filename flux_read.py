# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 13:19:35 2016

@author: HATLAB
"""

# Read sweep current data

# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:04:21 2015

@author: HatLab_Xi Cao
"""

# This is a test about how to read hdf5 outside the qtlab

#import hdf5_data as h5
import h5py

import matplotlib.pyplot as plt
import matplotlib.colors as color
import numpy as np

h5py_filepath = 'C:\\Qtlab\\'
h5py_filename = 'test'

fp2 = h5py.File(h5py_filepath + h5py_filename, 'r') 
#current = np.linspace(0,0.5,21)       working
current_data = fp2['current_data']
total_sweeps = len(current_data)
for i in range(total_sweeps):
    freq=fp2['f_data'+str(i)]           #  fdata changed to f_data
ar_freq = freq[:]
ar_current_data = [float(i) for i in current_data[:]]
#array = np.zeros([21,len(freq)])      working
array = np.zeros([total_sweeps,len(freq)])
#for i in range(21):                   working
for i in range(total_sweeps):
    #fdata = fp2['fdata'+str(i)]
    trace = fp2['trace_data'+str(i)][:]  # TODO tracedata changed to trace_data
    array[i]=trace[0]
    #print arrayName
    #plt.plot(fdata,trace[0])
    #print np.min(trace[0])

    #freq[i] = fdata[np.where(trace[0]<(np.min(trace[0])+0.000000001))[0][0]]/1e9

fp2.close()
# color map setting
levels=[180, 90, 0, -90, -180]
colors=[color.hex2color('#000000'), color.hex2color('#FF0000'), 
        color.hex2color('#FFFF00'), color.hex2color('#00FF00'),
        color.hex2color('#000000')]
levels=levels[::-1]
colors=colors[::-1]
_cmap=color.LinearSegmentedColormap.from_list('my_cmap', colors)
_norm=color.Normalize(vmin=-180, vmax=180)
print ar_current_data[0]
print ar_current_data[-1]
if ar_current_data[0] > ar_current_data[-1]:
    print 'here'
    array = array[::-1]
plt.imshow(array.transpose(), interpolation='nearest', aspect='auto', origin = 'lower', cmap=_cmap, norm=_norm)
#y=np.linspace(800, 950, 21)/100     working
y=np.linspace(ar_freq[0], ar_freq[-1], 21)/1e9

#y_space=[float(1601)/20*float(val) for val in range(len(y))]     working
y_space=[float(1601)/20*float(val) for val in range(len(y))]

plt.title('Plot from %s' % h5py_filename)
plt.yticks(np.array(y_space), y)
plt.ylabel('frequency(GHz)')

#plt.xticks(np.arange(21), current, rotation=90)            working
num_x_ticks = 20
x_ticks = np.arange(ar_current_data[0], ar_current_data[-1], (ar_current_data[-1] - ar_current_data[0])/num_x_ticks)
x_loc=[len(ar_current_data)/float(num_x_ticks)*i for i in range(num_x_ticks)]
plt.xticks(x_loc, x_ticks*1000, rotation=90)
plt.xlabel('Current (mA)')
plt.colorbar().set_label('phase(degrees)')
plt.show()
#plt.plot(current,freq,'*-')
#test = h5.HDF5Data(filepath=r"C:\Users\HatLab_Xi Cao\Box Sync\Data\VNA_qtlab_test_2016_06_07\\" , name='test01')
#test = h5.HDF5Data(filepath=r"C:\Qtlab\\" , name='flux_data5')
#print test['/S12 set'].value


#fdata = test['/fdata1']
#tracedata = test['/tracedata1']
#print tracedata
'''

r1=s11_1
r2=s12_1
r3=s21_1
r4=s22_1


theta1 = np.pi*s11_2/180
theta2 = np.pi*s12_2/180
theta3 = np.pi*s21_2/180
theta4 = np.pi*s22_2/180


ax = plt.subplot(2, 1, 1)
#ax = plt.subplot(1, 1, 1)
ax.set_title("Mag vs freq")

db20 = np.zeros(len(freq))
db20 = (1+db20)*-20

plt.plot(freq, r1, label="s11")
plt.plot(freq, r2, label="s12")
plt.plot(freq, r3, label="s21")
plt.plot(freq, r4, label="s22")

#plt.plot(freq, db20)

plt.plot(freq, r1, label="Ref_1_to_1")
plt.plot(freq, r2, label="Tran_2_to_1")
plt.plot(freq, r3, label="Tram_1_to_2")
plt.plot(freq, r4, label="Ref_2_to_2")

plt.legend(title="Mag", fancybox=True, loc="lower right")

ax = plt.subplot(2, 1, 2)

ax.set_title("Phase vs freq")


plt.plot(freq, theta1, label="s11")
plt.plot(freq, theta2, label="s12")
plt.plot(freq, theta3, label="s21")
plt.plot(freq, theta4, label="s22")


plt.legend(title="Phase", fancybox=True, loc="lower right")

plt.show()
'''

#test.close()