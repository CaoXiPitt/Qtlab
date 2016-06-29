# -*- coding: utf-8 -*-
"""
A driver to control the Yokogawa GS200 using Qtlab

@author: Hatlab - Erick Brindock
"""

from instrument import Instrument
import visa
import types
import logging
import numpy as np

class Yokogawa_GS200(Instrument):
                          
    def __init__(self, name, address, reset = False):
        """
        Initializes the Yokogawa GS200
            Input:
                name (string)    : name of the instrument
                address (string) : TCP/IP address
                reset (bool)     : resets to default values, default=False
        """
        logging.info(__name__ + ' : Initializing instrument Yokogawa GS200')
        Instrument.__init__(self, name, tags=['physical'])
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        self.add_parameter('output', type = types.IntType,
                           options_list = [0,1])
                           
        self.add_function('send_instruction')
        self.add_function('retrieve_data')
        
        
    def do_get_output(self):
        '''
        Reads the output state
            Output:
                state (int) : 0=OFF, 1=ON
        '''
        logging.info(__name__ + ' : Reading the output state')
        return self._visainstrument.write(':OUTP:STAT?')
        
    def do_set_output(self, enable = 1):
        '''
        Sets the state of the output
            Output:
                enable (int) : 0=OFF, 1=ON
        '''
        logging.info(__name__ + ' : Setting the output to %s' %enable)
        self._visainstrument.write(':OUTP:STAT %s' %enable)
        
    def send_instruction(self, command):
        print self._visainstrument.write(command)
        
    def retrieve_data(self, command):
        return self._visainstrument.ask(command)
