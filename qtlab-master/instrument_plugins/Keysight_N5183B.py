# -*- coding: utf-8 -*-
"""
A driver to control the Keysight MXG Analog Signal Generator N5183B using Qtlab

@author: Hatlab - Erick Brindock
"""
from instrument import Instrument
import visa
import types
import logging


class Keysight_N5183B(Instrument):
    OFF = 0
    ON = 1
    def __init__(self, name, address, reset=False):
        logging.info(__name__+ ' : Initializing Keysight N5183B')
        Instrument.__init__(self, name, tags=['physical'])
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        
        # Methods supported by both Signal Generators
        self.add_parameter('output_status', flags = Instrument.FLAG_GETSET,
                           type = types.StringType)
        self.add_parameter('frequency', flags = Instrument.FLAG_GETSET,
                           units = ' Hz', type = types.FloatType)
        self.add_parameter('reference_source', type = types.StringType,
                           flags = Instrument.FLAG_GET)
        self.add_parameter('alc_auto', flags = Instrument.FLAG_GETSET, 
                           type = types.IntType, options_list = [0,1])
        self.get_output_status()
        self.get_frequency()
        self.get_reference_source()
        self.get_alc_auto()
        
         # Phase
        self.add_parameter('phase_reference', flags = Instrument.FLAG_SET)
        self.add_parameter('phase_adjust', flags = Instrument.FLAG_GETSET,
                           units = 'DEG', type = types.FloatType)
        
        self.add_parameter('alc_bandwidth', flags = Instrument.FLAG_GETSET,
                           units = ' Hz', type = types.FloatType)
        self.add_parameter('alc_level', flags = Instrument.FLAG_GETSET,
                           units = ' dB', type = types.FloatType, 
                           minval = -20, maxval = 20)
       
        self.add_parameter('frequency_offset', flags = Instrument.FLAG_GETSET,
                           units = ' Hz', type = types.FloatType,
                           minval = -200e9, maxval = 200e9)
        
    def do_get_output_status(self):
        '''
        Reads the output status
            Output:
                The status of the output
        '''
        logging.info(__name__ + ' : getting output status')
        return self._visainstrument.ask('OUTP?')
    def do_set_output_status(self, enable):
        '''
        Enables/disables the RF output
            Input:
                enable (int) : on = 1, off = 0 
        '''
        logging.info(__name__ + ' : set output to %s' % enable)
        self._visainstrument.write('OUTP %s' % enable)
        
    def do_get_frequency(self):
        '''
        Reads the frequency of the signal
            Output:
                frequency (float) : in Hz
        '''
        logging.info(__name__+ ' : get frequency')
        return float(self._visainstrument.ask('FREQ:CW?'))
    def do_set_frequency(self, freq):
        '''
        Sets the frequency
            Input:
                freq (float) : Frequency in Hz
            Output:
                None
        '''
        logging.info(__name__ + ' : set frequency to %f' % freq)
        self._visainstrument.write('FREQ:CW %s' % freq)
        
    def do_get_reference_source(self):
        '''
        Reads the reference source
            Output:
                The source of the reference siganl
        '''
        return self._visainstrument.ask('ROSC:SOUR?')
    def do_set_reference_source(self, source):
        '''
        Sets the reference source
            Input:
                source (string) : INT = internal; EXT = external; BBG = internal baseband generator
        '''
        logging.info(__name__ + ' : set reference source to %s' % source)
        self._visainstrument.write('ROSC:SOUR %s' % source)

    def do_get_alc_auto(self):
        '''
        Reads the ALC auto status
            Output: 
                status (int) : ON=1 OFF=0
        '''
        logging.info(__name__+ ' get alc auto status')
        return self._visainstrument.ask('POW:ALC:BAND:AUTO?')
        
    def do_get_frequency_offset(self):
        '''
        Reads the frequency offset
            Output:
                frequency (float) : in Hz
        '''
        logging.info(__name__ = ' : get frequency offset')
        return self._visainstrument.ask('FREQ:OFF?')
    def do_set_frequency_offset(self, frequency):
        '''
        Sets the offset frequency
            Input:
                frequency (float) : in Hz
        '''
        logging.info(__name__ + ' : setting offset frequency to %f Hz' % frequency)
        self._visainstrument.write('FREQ:OFF %s' % frequency)
    def do_set_phase_reference(self):
        '''
        Sets the current output phase as a zero reference.
        '''
        logging.info(__name__ + ' : setting current phase output as zero reference')
        self._visainstrument.write('PHAS:REF')
    def do_get_phase_adjust(self):
        '''
        Reads the phase adjust of the modulating signal
        '''
        logging.info(__name__ + ' : get phase adjustment')
        return self._visainstrument.ask('PHAS:ADJ?')
    def do_set_phase_adjust(self, value):
        '''
        Sets the phase of the modulating signal
            Input:
                value (float) = -180 to 179 in degrees

        '''
        logging.info(__name__ + ' : setting phase adjust %f DEG' %value)
        self._visainstrument.write('PHAS:ADJ %sDEG' %value)
    def do_set_alc_level(self, value):
        '''
        Sets the automatic level control level
            Input: 
                value (float) : -20 to 20 dB
        '''
        logging.info(__name__ + ' : set alc power level %sDB' % value)
        self._visainstrument.write('POW:ALC:LEV %sDB' % value)



        
    def do_set_alc_bandwidth(self, width):
        '''
        Sets the ALC bandwidth
            Input:
                width (float) : frequency in Hz | width=AUTO : 2kHz
        '''
        logging.info(__name__+ ' : set alc bandwith to %s' % width)
        self._visainstrument.write('POW:ALC:BAND %s' % width)
    def do_get_alc_bandwidth(self):
        '''
        Reads the ALC bandwidth
            Output:
                bandwidth (float) : in Hz
        '''
        logging.info(__name__+ ' : get alc bandwidth')
        return float(self._visainstrument.ask('POW:ALC:BAND?'))
        
    