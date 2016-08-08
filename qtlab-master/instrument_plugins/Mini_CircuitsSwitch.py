# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 14:17:41 2016

@author: HatLab_Xi Cao
"""

# Switch control, make switch as an instrument
from instrument import Instrument
#import visa
import types
import logging
#import numpy as np
#import struct
import urllib2

#switch_address = 'http://169.254.47.255'
class Mini_CircuitsSwitch(Instrument):
    '''
    This is the driver for the Agilent E5071C Vector Netowrk Analyzer

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'AWG5014C', address='<GBIP address>, reset=<bool>')
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the Mini_Circuits switch, and communicates with the wrapper.

        Input:
          name (string)    : name of the instrument
          address (string) : http address
          reset (bool)     : resets to default values, default=False
        '''
        logging.info(__name__ + ' : Initializing instrument Mini_CircuitsSwitch')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        #self._visainstrument = visa.instrument(self._address) This switch does not use visa.
        self.add_parameter('portvalue',flags=Instrument.FLAG_GET,units='', type=types.StringType)
        
        self.add_function('set_switch')

        if (reset):
            self.reset()
        else:
            self.get_all()

    def get_all(self):
        '''
        Reads all implemented parameters from the instrument,
        and updates the wrapper.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : get all')
        #self.get_runningstate()
        
        self.get_portvalue()

    def set_switch(self,sw,state):
        '''
        sw: switch A through H or P if you want to control all the gates at same time
        state: 0 or 1 to choose output. 0=1 (green), 1=2 (red)        
        
        '''
        logging.info(__name__ + ' : Set switch%s' % sw +' to state %s' % state)
        if sw != 'P':
            ret = urllib2.urlopen(self._address + "/SET" + sw + "=" + state)
        else:
            if (len(state)) != 8:
                print len(state)
                raise Exception("Wrong input length!")
            newstate = 0
            for x in range(0,len(state)):
                if (int(state[x]) != 0) & (int(state[x]) != 1):
                    raise Exception("Wrong input value at %ith" % x + " switch!")
                else:
                    newstate += int(state[x])*(2**x)
            
  
            ret = urllib2.urlopen(self._address + "/SETP" + "=" + str(newstate))

        status = ret.readlines()[0]
        if status != '1':
            raise Exception("Switch didn't switch!")
        else:
            self.get('portvalue')
            
    def set_mode(self, mode):
        '''
        Mode is the name you want to send to the switch, like for S_signal_signal should be S_ss
        
        '''
        logging.info(__name__ + ' : Set the switch to measure %s' % mode)
        '''
        if mode == None:
            mode = str(raw_input('Enter the mode name: (e.g S_ss) \n'))
        else:
            pass
        '''
        
        if mode == 'S_ss':
            self.set_switch('P','00010110')
        elif mode == 'S_ii':
            self.set_switch('P','01010010')
        elif mode == 'S_pp':
            self.set_switch('P','00001000')
        elif mode == 'S_si':
            self.set_switch('P','0001  ')
        elif mode == 'S_is':
            self.set_switch('P','01010110')
        elif mode == 'S_ip':
            self.set_switch('P','01011000')
        elif mode == 'S_pi':
            self.set_swtich('P','00000010')
        elif mode == 'S_ps':
            self.set_switch('P','00000110')
        elif mode == 'S_sp':
            self.set_switch('P','00011000')
        elif mode == 'S_rr':
            self.set_switch('P','10000011')
            
        
    def do_get_portvalue(self):
        logging.debug(__name__+' : get portvalue')
        ret = urllib2.urlopen(self._address + "/SWPORT?" )
        result = ret.readlines()[0]
        result = int(result)
        result = format(result,'08b')
        result = result[::-1]
        return result
        
        
        
        
        
        
        
        
        
        
        
        
        