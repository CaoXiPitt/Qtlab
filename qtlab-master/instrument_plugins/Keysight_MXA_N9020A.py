# -*- coding: utf-8 -*-
"""
A driver to control the Keysight MXA Signal Analyzer N9020A using Qtlab

@author: Hatlab - Erick Brindock
"""

from instrument import Instrument
import visa
import types
import logging
import numpy as np

class Keysight_MXA_N9020A(Instrument):
    
    def __init__(self, name, address, reset = False):
        """
        Initializes the Keysight MXA N9020A
            Input:
                name (string)    : name of the instrument
                address (string) : GPIB address
                reset (bool)     : resets to default values, default=False
        """
        logging.info(__name__ + ' : Initializing instrument Keysight MXA N9020A')
        Instrument.__init__(self, name, tags=['physical'])
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        self.add_parameter('frequency_center', type = types.FloatType, 
                           units = ' Hz')
        self.add_parameter('frequency_start', type = types.FloatType,
                           units = ' Hz')
        self.add_parameter('frequency_stop', type = types.FloatType,
                           units = ' Hz')
        self.add_parameter('frequency_span', type = types.FloatType,
                           units = ' Hz')
        self.add_parameter('bandwidth_res', type = types.FloatType,
                           units = ' Hz')
        self.add_parameter('bandwidth_res_auto', type = types.IntType,
                           options_list = [0,1])
        self.add_parameter('bandwidth_video', type = types.FloatType,
                           minval = 1, maxval = 50000000)
        self.add_parameter('bandwidth_video_auto', type = types.IntType,
                           options_list = [0,1])                   
        self.add_parameter('trigger_source', type = types.StringType,
                           options_list = ['ext1', 'external1', 'ext2', 'external2',
                                           'imm', 'immediate'])

        self.add_parameter('trace', type=types.ListType)
        self.add_parameter('trace_type', type=types.StringType,
                           options_list = ['writ', 'write', 'aver', 'average',
                                           'maxh', 'maxhold', 'minh', 'minhold'])
        self.add_function('get_all')
        self.get_all()
            
    def do_get_frequency_center(self):
        '''
        Reads the frequency center
            Output:
                frequency_center (float) : center frequency in Hz
        '''
        logging.info(__name__ + ' : Getting frequency center')
        return self._visainstrument.ask('FREQ:CENT?')
        
    def do_set_frequency_center(self, frequency):
        """
        Sets the center frequency of the graticle. The span is held constant, 
        while the start and stop are changed.
            Input: 
                frequency (float) : location of the center frequency in Hz
        """
        logging.info(__name__ + ' : Setting frequency to %f' %frequency)
        return self._visainstrument.write('FREQ:CENT %f' %frequency)
        
    def do_get_frequency_start(self):
        """
        Reads the starting (left side) frequency of the graticle
            Output:
                frequency (float) : value of starting frequency in Hz
        """
        logging.info(__name__ + ' : Reading start frequency')
        return self._visainstrument.ask('FREQ:STAR?')
        
    def do_set_frequency_start(self, frequency):
        '''
        Sets the starting (left side) frequency of the graticle. The stop frequency
        is held constant, while the center frequency and span will change
            Input:
                frequency (float) : value of the starting frequency in Hz
        '''
        logging.info(__name__ + ' : Setting start frequency to %f' %frequency)
        self._visainstrument.write('FREQ:STAR %f' %frequency)
    
    def do_get_frequency_stop(self):
        '''
        Reads the stop (right side) frequency of the graticle
            Output:
                frequency (float) : value ofstop frequency in Hz
        '''
        logging.info(__name__ + ' : Reading stop frequency')
        return self._visainstrument.ask('FREQ:STOP?')
        
    def do_set_frequency_stop(self, frequency):
        '''
        SEts the stop (right side) frequency of the graticle. The start frequency
        is held constant, while the center and span are changed.
            Input:
                frequency (float) : value fo stop frequency in Hz
        '''
        logging.info(__name__ + ' : Setting stop frequency to %f' %frequency)
        self._visainstrument.write('FREQ:STOP %f' %frequency)
        
    def do_get_frequency_span(self):
        '''
        Reads the span of the frequency sweep
            Output:
                frequency (float) : span of the sweep in Hz
        '''
        logging.info(__name__ + ' : Reading the frequency span')
        return self._visainstrument.ask('FREQ:SPAN?')
        
    def do_set_frequency_span(self, span):
        '''
        Sets the span of the frequency sweep. The center is held constant,
        while the start and stop are changed.
            Input:
                range (float) : 
        '''
        logging.info(__name__ + ' : Setting the frequency span %f' %span)
        self._visainstrument.write('FREQ:SPAN %f' %span)   
    
    def do_get_bandwidth_res(self):
        '''
        Reads the bandwidth resolution
            Output: 
                bandwidth (float) : resolution of bandwidth in Hz
        '''
        logging.info(__name__ + ' : Reading the bandwitdth resolution')
        return self._visainstrument.ask('BAND?')
    
    def do_set_bandwidth_res(self, resolution):
        '''
        Sets the resolution of the bandwidth
        Note:Only certain discrete resolution bandwidths are available. The available bandwidths
        are dependent on the Filter Type or the EMC Standard. If an unavailable bandwidth
        is entered with the numeric keypad, the closest available bandwidth is selected.
            Input:
                resolution (float) : resolution of bandwidth in Hz
        '''
        logging.info(__name__ + ' : Setting bandwidth resolution to %f' %resolution)
        self._visainstrument.write('BAND %f' %resolution)
        
    def do_get_bandwidth_res_auto(self):
        '''
        Reads the state of bandwidth coupling
            Output:
                state (int) : 0 = OFF, 1 = ON
        '''
        logging.info(__name__ + ' : Reading the state bandwidth coupling')
        return self._visainstrument.ask('BAND:AUTO?')
        
    def do_set_bandwidth_res_auto(self, enable):
        '''
        Sets the state of bandwidth coupling
            Input:
                state (int) : 0 = OFF, 1 = ON
        '''
        logging.info(__name__ + ' : Setting the bandwidth coupling to %s' %enable)
        self._visainstrument.write('BAND:AUTO %s' %enable)
    
    def do_get_bandwidth_video(self):
        '''
        Reads the post-detection filter frequency
            Output:
                frequency (float) : video bandwidth in Hz
        '''
        logging.info(__name__ + ' : Reading the video bandwidth')
        return self._visainstrument.ask('BAND:VID?')
        
    def do_set_bandwidth_video(self, frequency):
        '''
        Sets the video bandwidth frequency
            Input:
                frequency (float) : video band width in Hz (from 1 Hz to 8MHz)
                (set to 50 MHz for wide open video filter)
        '''
        if frequency > 8000000 and frequency < 50000000:
            frequency = 8000000
        logging.info(__name__ + ' : Setting the video bandwidth to %f' %frequency)        
        self._visainstrument.write('BAND:VID %f' %frequency)
        
    def do_get_bandwidth_video_auto(self):
        '''
        Reads the state of the video bandwith coupling
            Output:
                state (int) : 0 = OFF, 1= ON
        '''
        logging.info(__name__ + ' : Reading the state of the video bandwidth')
        return self._visainstrument.ask('BAND:VID:AUTO?')
    def do_set_bandwidth_video_auto(self, enable):
        '''
        Sets the video bandwidth coupling to auto
            Input:
                enable (int) : 0=OFF, 1=ON
        '''
        logging.info(__name__ + ' : Setting the VBW coupling to %s' %enable)
        self._visainstrument.write('BAND:VID:AUTO %s' % enable)
        
    def do_get_trigger_source(self):
        '''
        Reads the source of the trigger
            Output:
                source (string) : source of triggering
        '''
        logging.info(__name__ + ' : Reading the triggering source')
        return self._visainstrument.ask('TRIG:SOUR?')
        
    def do_set_trigger_source(self, source):
        '''
        Sets the source of the trigger
            Input:
                source (string) : the source to be used as the trigger
        '''
        source = source.lower()
        logging.info(__name__ + ' : Setting the source of the trigger to %s' % source)
        self._visainstrument.write('TRIG:SOUR %s' %source)
    

    def do_get_trace(self, channel):
        return self._visainstrument.ask('TRAC%s:DISP?' %channel)
    def do_set_trace(self, channel):
        self._visainstrument.write('TRAC{}:DISP {}'.format(channel[0], channel[1]))
        
    def do_get_trace_type(self, channel):
        return self._visainstrument.ask('TRAC{}:TYPE?'.format(channel))
    def do_set_trace_type(self, channel = 1, trace_type):
        trace_type = trace_type.lower()
        self._visainstrument.write('TRAC{}:TYPE {}'.format(channel, trace_type))
        
    def get_all(self):
        self.get_frequency_center()
        self.get_frequency_start()
        self.get_frequency_stop()
        self.get_frequency_span()
        self.get_bandwidth_res()
        self.get_bandwidth_res_auto()
        self.get_bandwidth_video()
        self.get_bandwidth_video_auto()
        self.get_trigger_source()
        
        
