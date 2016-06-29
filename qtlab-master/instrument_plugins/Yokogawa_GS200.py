# -*- coding: utf-8 -*-
"""
A driver to control the Yokogawa GS200 using Qtlab

@author: Hatlab - Erick Brindock
"""

from instrument import Instrument
import visa
import types
import logging
import time
import threading
import numpy as np

MIN_CURR = 1E-3
MAX_CURR = 200E-3

class Yokogawa_GS200(Instrument):
                          
    def __init__(self, name, address, source_type = 'current', reset = False):
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
        self.add_parameter('output_function', type = types.StringType,
                           options_list = ['curr', 'current'])
        self.add_parameter('output_range', type = types.StringType,
                           units = ' A')
        self.add_parameter('output_level', type = types.StringType)
        self.add_parameter('output_level_auto', type = types.StringType)
        self.add_parameter('output_protection', type = types.StringType)

        self.add_function('test_program_function')
        self.add_function('create_csv')
        self.add_function('set_intervals')
        self.add_function('save_setup')
        self.add_function('load_setup')           
        self.add_function('send_instruction')
        self.add_function('retrieve_data')
        self.add_function('reset')
        self.add_function('get_all')
        self.write_termination = None
        self.ask_termination = None
        
        if reset:
            self.reset()
        #else:
            #self.get_all()

##  Parameters  ###############################################################
               
    def do_get_output(self):
        '''
        Reads the output state
            Output:
                state (int) : 0=OFF, 1=ON
        '''
        self._log('Reading the output state')
        return self._visainstrument.ask(':OUTP:STAT?')
        
    def do_set_output(self, enable = 1):
        '''
        Sets the state of the output
            Output:
                enable (int) : 0=OFF, 1=ON
        '''
        self._log('Setting the output to %s' %enable)
        self._visainstrument.write(':OUTP:STAT %s' %enable)
    
    def do_get_output_function(self):
        '''
        Gets the output function
            Output:
                function (string) : whether the outout is set for current or
                voltage
        '''
        self._log('Reading the output function')
        return self._visainstrument.ask(':sour:func?')
    def do_set_output_function(self):
        '''
        Sets the output to current 
        '''
        self._log('Setting the output function to current')
        self._visainstrument.write(':sour:func curr')
    
    def do_get_output_range(self):
        '''
        Reads the range of the output
            Output:
               range (string) : source range in A
        '''
        self._log('Reading the output range')
        return self._visainstrument.ask(':sour:rang?')
        
    def do_set_output_range(self, _range):
        '''
        Sets the range of the output
            Input:
                range (string | <float>) : the range of the source, acceptable 
                values are:  max | min | up | down | <level> in A    
        '''
        possible_strings = ['max', 'min', 'up', 'down']
        self._check_input_validity(_range, possible_strings, 
                                  MIN_CURR, MAX_CURR)
        self._log('Setting the output range to %s' %_range)
        self._visainstrument.write(':sour:rang %s')
    
    def do_get_output_level(self):
        '''
        Reads the source level in terms of the range being used
            Output:
                level (string) : max | min | <level>
        '''
        self._log('Reading the source level')
        return self._visainstrument.ask(':sour:lev?')
    def do_set_output_level(self, level):
        '''
        Sets the source level in terms of the range being used
            Input:
                level (string | <float>) : level produced max | min | <level>
        '''
        possible_strings = ['max', 'min']
        self._check_input_validity(level, possible_strings)
        self._log('Setting the source level to %s' %level)
        self._visainstrument.write(':sour:lev %s' %level)
        
    def do_get_output_protection(self):
        '''
        Reads the current limiter level
            Output:
                limit (string) : current limit level max | min | <level>
        '''
        self._log('Reading the current limit level')
        self._visainstrument.ask(':sour:prot:curr?')
    def do_set_output_protection(self, limit):
        '''
        Sets the current limit level
            Input:
                limit (string) : max | min | <level>
        '''
        self._check_input_validity(limit, ['min','max'], MIN_CURR, MAX_CURR)
        self._log('Setting the current limit to %s' % limit)
        self._visainstrument.write(':sour:prot:curr %s' % limit)
##  Functions  ###############################################################
        
    def save_setup(self, filename):
        '''
        Saves the system's setup data
            Input:
                filename (string) : name of file to save to
        '''
        self._log('Saving system data to %s' % filename)
        self._visainstrument.write(':syst:set:save %s' %filename)
        
    def load_setup(self, filename):
        '''
        Restores the system's setup
            Input:
                filename (string) : name of the file to be restored
        '''
        self._log('Restoring system state from file %s' % filename)
        self._visainstrument.write(':syst:set:load %s' % filename)
    def send_instruction(self, command):
        '''
        Sends a generic instrucion to the unit
            Input:
                command (string) : see User's Manual for specific commands and 
                their behavior
        '''
        self._visainstrument.write(command)
        
    def retrieve_data(self, command):
        '''
        Reads data from the unit
            Input:
                command (string) : see User's Manual for specifc commands and 
                the values returned
            Output:
               value (varied) : see User's Manual for specific commands and 
               the values returned
        '''
        return self._visainstrument.ask(command)
        
    def reset(self):
        '''
        Resets the unit do default settings, and sets the output to current
        '''
        self._log('Resetting the instrument')
        self._visainstrument.write('*RST;:sour:func curr')
    
    def get_all(self):
        self.get_output()
        self.get_output_function()
        self.output_range()
        self.output_level()
        self.output_level_auto()
        self.output_protection()

##  Helpers  #################################################################
    def _log(self, string):
        logging.info(__name__ + ' : ' + string)
        
    def _check_input_validity(testval, strings, minval = None, maxval = None):
        try:
            testval = float(testval)
            if (minval is not None) and testval < minval:
                raise ValueError('Min')
            if maxval is not None and testval > maxval:
                raise ValueError('Max')
        except:
            if testval.lower() not in strings:
                raise ValueError('%s is not a valid input' %testval)
        return testval
        
    def create_csv(self, step = 1e-3, minval=.001, maxval=.2):
        '''
        creates a list of currents formatted to be transferred to the Yokogawa 
        unit
            Input:
                step (float) : the interval between current levels (note:
                negative values will count down from maxval to minval)
                minval (float) : the minimum value for the current to start at
                maxval (float) : the maximum value for the current to reach
            Output:
                csv_values (string) : 
                of the form '<level>, <range>, <output type>' 
        '''
        string = ''
        source_range = .200
        source_type = 'I'
        if step>0:
            value = minval
            while value < maxval:
                string += '{},{},{}\n'.format(value, source_range, 
                                                source_type)
                value += step
            string += '{},{},{}\n'.format(maxval, source_range, source_type)
        else:
            value = maxval
            while value > minval:
                string += '{},{},{}\n'.format(value, source_range, 
                                                source_type)
                value += step
            string += '{},{},{}\n'.format(minval, source_range, source_type)
        return string
        
    def set_intervals(self, step = .001, rate = .001, time_at_level = 0):
        slope_time = step/rate
        interval = slope_time + time_at_level
        self._visainstrument.write(':prog:int {};slope {}'.format(interval,
                                                                  slope_time))
    def test_program_function(self):
        self.set_intervals()
        self._visainstrument.write(':outp on;:prog:mem "%s";run' %self.create_csv())
