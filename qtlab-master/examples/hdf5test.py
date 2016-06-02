# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 16:56:35 2015

@author: HatLab_Xi Cao
"""

import hdf5_data as h5

import qt

VNA = qt.instruments['VNA']

trform_old = VNA.get_trform()
sparam_old = VNA.get_sparam()

### Direct access to hdf5 container

# create data; follows the data storage scheme of qtlab
dat = h5.HDF5Data(filepath=r"C:\Users\HatLab_Xi Cao\Box Sync\Programming\Olivia_cable\\" , name='Olivia_cable_TX03_10')


# this function is a simple wrapper for the h5py method of the same name
print 'create our first dataset'

test=h5.HDF5Data.get_filepath(dat)
print test

VNA.set_trform('PLOG')

dset_f = dat.create_dataset('freqvalues',(1,1601),'d')
dset_f[...] = VNA.getfdata()
print dset_f.value


VNA.set_sparam('S11')
qt.msleep(1)
dset1 = dat.create_dataset('S11 set',(2,1601),'d')
dset1[...] = VNA.gettrace()
print dset1 # this is the dataset object
print dset1.value # this is a numpy array

VNA.set_sparam('S12')
qt.msleep(1)
dset2 = dat.create_dataset('S12 set',(2,1601),'d')
dset2[...] = VNA.gettrace()
print dset2 # this is the dataset object
print dset2.value # this is a numpy array

VNA.set_sparam('S21')
qt.msleep(1)
dset3 = dat.create_dataset('S21 set',(2,1601),'d')
dset3[...] = VNA.gettrace()
print dset3 # this is the dataset object
print dset3.value # this is a numpy array

VNA.set_sparam('S22')
qt.msleep(1)
dset4 = dat.create_dataset('S22 set',(2,1601),'d')
dset4[...] = VNA.gettrace()
print dset4 # this is the dataset object
print dset4.value # this is a numpy array

VNA.set_trform(trform_old)
VNA.set_sparam(sparam_old)

dat.close()