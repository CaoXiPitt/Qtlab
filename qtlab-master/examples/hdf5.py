"""
Example to illustrate the usage of the hdf5_data module;
To check out the resulting file, you can use, besides python,
the HDFView Program from the HDF group (hdfgroup.com).

About HDF5 implementation in python see h5py.alfven.org.

Latest version: 2012/12/26, Wolfgang Pfaff <wolfgangpfff at gmail dot com>
"""

import hdf5_data as h5
import numpy as np

### Direct access to hdf5 container

# create data; follows the data storage scheme of qtlab
#fname='Michael is so behind on papework'
#print fname

#dat = h5.HDF5Data(name=fname)

#dat = h5.HDF5Data(name='data_number_one')
dat = h5.HDF5Data(filepath=r'C:/Users/HatLab_Xi Cao/Desktop',name='test')
print 'create our first dataset'

test=h5.HDF5Data.get_filepath(dat)
print test

#print dat._filepath
# this function is a simple wrapper for the h5py method of the same name
#print 'create our first dataset'
dset1 = dat.create_dataset('first set', (5,5), 'i')
dset1[...] = 42
#print dset1 # this is the dataset object
#print dset1.value # this is a numpy array

# simpler access (equivalent)
#print ''
#print 'again...'
#print dat['/first set']

# create something in a group, by simple access (there's also a create_group
# method that's a simple wrapper for the h5py method).
#print ''
#print 'more data...'

# On new versions of h5py you don't have to explicitly create the groups,
# but you can set an array in any group you like.
arr = np.arange(16).reshape((4,4))
g1 = dat.create_group('my first group')
g2 = g1.create_group('my first subgroup')
dat['/my first group/my first subgroup/an array'] = arr
#print dat['/my first group']
#print dat['/my first group/my first subgroup']
#print dat['/my first group/my first subgroup/an array'].value

# set some metadata
# any stuff can be attribute to data sets and groups; any kind of data that
# fits into numpy arrays can be stuffed in there.
dat['/my first group'].attrs['description'] = 'an utterly pointless group'
dat['/my first group'].attrs['yo mama'] = 'probably fat'
dat['/my first group/my first subgroup/an array'].\
        attrs['unit'] = 'TT'
dat['/my first group/my first subgroup/an array'].\
        attrs['ridiculously large magnetic fields'] = True

# don't forget closing! (ends up unreadable otherwise)
dat.close()
'''
abc = h5.HDF5Data(name=fname)
#print "if this works"
#print abc['/my first group']
#print abc['/my first group/my first subgroup/an array'].value
#print "we win!"
abc.close()
'''