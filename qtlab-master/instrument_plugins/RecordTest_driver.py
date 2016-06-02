# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 13:45:51 2016

@author: HatLab_Xi Cao
"""

# Test driver for the recordtest

from instrument import Instrument
import types
import logging

class RecordTest_driver(Instrument):

    def __init__(self, name, address=None, reset=False):
        Instrument.__init__(self, name, tags=['measure', 'example'])

        # minimum
        self.add_parameter('value1', type=types.FloatType,
                flags=Instrument.FLAG_GET)


        # set bounds and limit rate (stepdelay in ms)
        self.add_parameter('output1', type=types.FloatType,
                flags=Instrument.FLAG_SET,
                minval=0, maxval=10,
                maxstep=0.01, stepdelay=50)



        self.add_function('reset')
        self.add_function('get_all')
        #self.add_function('step')

        # dummy values for simulating instrument
        self._dummy_value1 = 1.1
        self._dummy_value2 = 1.2
        self._dummy_output1= 1.3
        self._dummy_status = 'off'
        self._dummy_speed = 2
        self._dummy_input = [1, 4, 9, 16]
        self._dummy_output = {'A':0, 'B':1, 'C':2}
        self._dummy_gain = 10

        if address == None:
            raise ValueError('Example Instrument requires an address parameter')
        else:
            print 'Example Instrument  address %s' % address

        if reset:
            self.reset()
        else:
            self.get_all()

    def reset(self):
        """Reset example instrument"""

        logging.info('Resetting example instrument')

        self.set_output1(1.5)


        return True

    def get_all(self):

        self.get_value1()
        #self.get_output1()

        return True

    def do_get_value1(self):
        return self._dummy_value1


    def do_set_output1(self, val):
        self._dummy_output1 = val


    '''
    def step(self, channel, stepsize=0.1):
   #     Step channel <channel>
        print 'Stepping channel %s by %f' % (channel, stepsize)
        cur = self.get('ch%s_output' % channel, query=False)
        self.set('ch%s_output' % channel, cur + stepsize)
    '''
