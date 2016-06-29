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
#list for accepted values for functions
TRACE_MODES = ['ON', 'VIEW', 'BLANK', 'BACKGROUND']
TRACE_TYPES = ['writ', 'write', 'aver', 'average', 'maxh', 'maxhold', 
               'minh', 'minhold']
TRACE_DETECTORS = ['aver', 'average', 'neg', 'negative', 'norm', 'normal', 
                       'pos', 'positive', 'samp', 'sample', 'qpe', 'qpeak', 
                       'eav', 'eaverage', 'rav', 'raverage']
class Keysight_MXA_N9020A(Instrument):
                          
    def __init__(self, name, address, reset = False):
        """
        Initializes the Keysight MXA N9020A
            Input:
                name (string)    : name of the instrument
                address (string) : TCP/IP address
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
                           options_list = ['ext1', 'external1', 'ext2', 
                           'external2', 'imm', 'immediate'])                                   
        self.add_parameter('sweep_time', type = types.FloatType,
                           units = ' s', minval = 1e-6, maxval = 6000)
        self.add_parameter('sweep_time_auto', type = types.IntType,
                           options_list = [0,1])
        self.add_parameter('sweep_time_auto_rules', type = types.StringType,
                           options_list = ['norm', 'normal', 'accuracy',
                                           'acc', 'sres', 'sresponse'])
        self.add_parameter('continous_measurement', type = types.IntType,
                           options_list = [0,1])                                  
        self.add_parameter('trace_1', flags = Instrument.FLAG_GET, 
                           type = types.ListType)
        self.add_parameter('trace_2', flags = Instrument.FLAG_GET, 
                           type = types.ListType)
        self.add_parameter('trace_3', flags = Instrument.FLAG_GET, 
                           type = types.ListType)
        self.add_parameter('trace_4', flags = Instrument.FLAG_GET, 
                           type = types.ListType)
        self.add_parameter('trace_5', flags = Instrument.FLAG_GET, 
                           type = types.ListType)
        self.add_parameter('trace_6', flags = Instrument.FLAG_GET, 
                           type = types.ListType)
                                                      
        self.add_function('trace_on')
        self.add_function('trace_view')
        self.add_function('trace_blank')
        self.add_function('trace_background')
        self.add_function('trace_detector')
        self.add_function('trace_type')
        self.add_function('clear_trace')

        self.add_function('set_max_count')
        self.add_function('get_data')
        self.add_function('get_previous_data')
        self.add_function('get_average')                                  
        self.add_function('get_all')
        self.add_function('reset')
        self.add_function('send_command')
        self.add_function('retrieve_data')
        
        if reset:
            self.reset()
        else:
            self.get_all()

    def set_max_count(self, maxval):
        '''
        Sets the hold value
            Input: 
                maxval (int) : the number of averages taken (note: Only stops 
                if in Single measurement mode. See XNA-manual pg. 617 for more 
                information on continous mode averaging behavior)
        '''
        logging.info(__name__ + ' Setting the max hol count to %s' %maxval)
        self._visainstrument.write('AVER:COUN %s' %maxval)
        
    def do_set_continous_measurement(self, enable = 1):
        '''
        Sets the measurement mode to continous or single
            Input:
                enable (int) : 0=Single, 1=Continous
        '''
        logging.info(__name__ + ' Setting the measurement mode to %s' %enable)
        self._visainstrument.write('INIT:CONT %s' %enable)
        
    def do_get_continous_measurement(self):
        '''
        Reads the continous measurement state
            Output:
                state (int) : 0=Single, 1=Continous
        '''
        logging.info(__name__ + ' Reading the measurement mode')
        return self._visainstrument.ask('INIT:CONT?')
        
    def get_data(self, count = 0, channel = 1):
        '''
        Reads the data from the current sweep (NEEDS TESTED)
            Input:
                count (int) : sets max hold value between 1 and 10,000
                0 uses the value stored in the instrument
                channel (int):
            Output:
                data (numpy 2dArray) : [x, y] values
        '''
        data = None
        if count is not 0:
            if count > 10000:
                count = 10000
                logging.warning(__name__ +
                                ' Count too high. set to max value 10000')            
            self._visainstrument.write('AVER:COUN %s' % count)
        if channel < 1 or channel > 6:
            raise ValueError('channel must be between 1 and 6')
        else:
            self._visainstrument.write('AVER:CLE')
        while data is None:
            try:
                data = self._visainstrument.ask('CALC:DATA%s?' % channel)
            except Exception as e:
                print ('Running test.')
                logging.info(__name__ + str(type(e)) + 
                            ' raised. Count not done')
            else:
                print('Count complete')
                logging.info(__name__ + ' Reading the trace data')
                data = data.lstrip('[').rstrip(']').split(',')
                data = [float(value) for value in data]
                np_array = np.reshape(data, (-1,2))
                return np_array
                
    def get_previous_data(self, channel = 1):
        '''
        Reads the data already acquired without starting a new test
        '''
        return self._visainstrument.ask('CALC:DATA%s?' %channel)           
                
    def get_average(self):
        '''
        Reads the average of the current sweep
            Output: 
                average (float) :the average
        '''
        logging.info(__name__ + ' Reading the average value')
        return self._visainstrument.ask('CALC:DATA:COMP? MEAN')
    def trace_type(self, trace_type, channel = 1):
        '''
        Sets the type of the trace on the specified channel
            Input:
                trace_type (string) : 
                    ['writ', 'write', 'aver', 'average', 'maxh', 'maxhold', 
                     'minh', 'minhold']
                channel (int) : channel 1-6
        '''
        self.is_valid_channel(channel)
        trace_type = trace_type.lower()
        if trace_type not in TRACE_TYPES:
            raise ValueError('%s is not a valid trace type' % trace_type)
        logging.info(__name__ + 
            ' setting trace type to {} on channel {}'.format(trace_type,
                                                            channel))
        self._visainstrument.write('TRAC{}:TYPE {}'.format(channel, 
                                                           trace_type))
        
    def trace_detector(self, detector, channel = 1):
        '''
        Sets the detector for the trace on the specified channel
            Input:
                detector (string) : 
                    ['aver', 'average', 'neg', 'negative', 'norm', 'normal', 
                    'pos', 'positive', 'samp', 'sample', 'qpe', 'qpeak', 'eav',
                    'eaverage', 'rav', 'raverage']
                channel (int) : channel 1-6
        '''
        self.is_valid_channel(channel)
        if detector not in TRACE_DETECTORS:
            raise ValueError('%s is not a valid detector type' % detector)
        logging.info(__name__ + 
            ' setting the detector to {} for channel {}'.format(detector,
                                                                channel))
        self._visainstrument.write('DET:TRAC{} {}'.format(channel, detector))
        
    def do_get_trace_1(self):
        '''
        Reads the style of trace 1
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 1')
        return ['Disp: ' + self._visainstrument.ask('TRAC1:DISP?'),
                'Upd: ' + self._visainstrument.ask('TRAC1:UPD?'),
                'Type: ' + self._visainstrument.ask('TRAC1:TYPE?'),
                'Det: ' + self._visainstrument.ask('DET:TRAC1?')]
    
    def do_get_trace_2(self):
        '''
        Reads the style of trace 2
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 2')
        return ['Disp: ' + self._visainstrument.ask('TRAC2:DISP?'),
                'Upd: ' + self._visainstrument.ask('TRAC2:UPD?'),
                'Type: ' + self._visainstrument.ask('TRAC2:TYPE?'),
                'Det: ' + self._visainstrument.ask('DET:TRAC2?')]
    
    def do_get_trace_3(self):
        '''
        Reads the style of trace 3
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 3')
        return ['Disp: ' + self._visainstrument.ask('TRAC3:DISP?'),
                'Upd: ' + self._visainstrument.ask('TRAC3:UPD?'),
                'Type: ' + self._visainstrument.ask('TRAC3:TYPE?'),
                'Det: ' + self._visainstrument.ask('DET:TRAC3?')]
    
    def do_get_trace_4(self):
        '''
        Reads the style of trace 4
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 4')
        return ['Disp: ' + self._visainstrument.ask('TRAC4:DISP?'),
                'Upd: ' + self._visainstrument.ask('TRAC4:UPD?'),
                'Type: ' + self._visainstrument.ask('TRAC4:TYPE?'),
                'Det: ' + self._visainstrument.ask('DET:TRAC4?')]
    
    def do_get_trace_5(self):
        '''
        Reads the style of trace 5
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 5')
        return ['Disp: ' + self._visainstrument.ask('TRAC5:DISP?'),
                'Upd: ' + self._visainstrument.ask('TRAC5:UPD?'),
                'Type: ' + self._visainstrument.ask('TRAC5:TYPE?'),
                'Det: ' + self._visainstrument.ask('DET:TRAC5?')]
    
    def do_get_trace_6(self):
        '''
        Reads the style of trace 6
            Output:
                values (list) : [Display, Update, Type, Detector] ON = 1 OFF =2
        '''
        logging.info(__name__ + ' Reading state of trace 6')
        return ['Disp: ' + self._visainstrument.ask('TRAC6:DISP?'),
                'Upd: ' + self._visainstrument.ask('TRAC6:UPD?'),
                'Type: ' + self._visainstrument.ask('TRAC6:TYPE?'),
                'Det: ' + self._visainstrument.ask('DET:TRAC6?')]
                
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
        Sets the starting (left side) frequency of the graticle. The stop 
        frequency is held constant, while the center frequency and span will 
        change
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
        Sets the stop (right side) frequency of the graticle. The start 
        frequency is held constant, while the center and span are changed.
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
        Note:Only certain discrete resolution bandwidths are available. 
        The available bandwidths are dependent on the Filter Type or the EMC 
        Standard. If an unavailable bandwidth is entered with the numeric 
        keypad, the closest available bandwidth is selected.
            Input:
                resolution (float) : resolution of bandwidth in Hz
        '''
        logging.info(__name__ + 
                    ' : Setting bandwidth resolution to %f' %resolution)
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
        logging.info(__name__ + 
                    ' : Setting the bandwidth coupling to %s' %enable)
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
        logging.info(__name__ + 
            ' : Setting the video bandwidth to %f' %frequency)        
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
        logging.info(__name__ + 
                    ' : Setting the source of the trigger to %s' % source)
        self._visainstrument.write('TRIG:SOUR %s' %source)
    
    def trace_on(self, channel = 1):
        '''
        Sets the trace mode to ON (ie Display on, Update on)
            Input:
                channel (int) : channel to alter [1-6]
        '''
        logging.info(__name__ + ' Setting channel %s to on' %channel)
        self._visainstrument.write('TRAC%s:UPD 1' % channel)
        self._visainstrument.write('TRAC%s:DISP 1' % channel)
                
    def trace_view(self, channel = 1):
        '''
        Sets the trace mode to VIEW (ie Display on, Update off)
            Input:
                channel (int) : channel to alter [1-6]
        '''
        logging.info(__name__ + ' Setting channel %s to view' %channel)
        self._visainstrument.write('TRAC%s:UPD 0' %channel)
        self._visainstrument.write('TRAC%s:DISP 1' %channel)
        
    def trace_blank(self, channel = 1):
        '''
        Sets the trace mode to BLANK (ie Display off, Update off)
            Input:
                channel (int) : channel to alter [1-6]
        '''
        logging.info(__name__ + ' Setting channel %s to blank' %channel)
        self._visainstrument.write('TRAC%s:UPD 0' %channel)
        self._visainstrument.write('TRAC%s:DISP 0' %channel)
        
    def trace_background(self, channel = 1):
        '''
        Sets the trace mode to BACKGROUND (ie Display off, Update on)
            Input:
                channel (int) : channel to alter [1-6]
        '''
        logging.info(__name__ + ' Setting channel %s to background' %channel)
        self._visainstrument.write('TRAC%s:UPD 1' %channel)
        self._visainstrument.write('TRAC%s:DISP 0' %channel)
        
    def clear_trace(self, *trace_channel):
        '''
        Clears the specified trace without effecting state of function or 
        variable
            Input:
                trace_channel (int) : 1|2|3|4|5|6 channel to be cleared
        '''
        logging.info(__name__ + ' Clearing the trace')
        for i in trace_channel:
            self._visainstrument.write('TRAC:CLE TRACE%s' %i)
            
    def do_get_sweep_time(self):
        '''
        Reads the sweep time of the current frequency span
            Output:
                time (float) : in seconds
        '''
        logging.info(__name__ + ' Reading sweep time')
        return self._visainstrument.ask('SWE:TIME?')

    def do_set_sweep_time(self, time):
        '''
        Sets the sweep time of the current frequency span
            Input:
                time (float): in seconds
        '''
        logging.info(__name__ + ' Setting sweep time to %s' %time)
        self._visainstrument.write('SWE:TIME %s' %time)  
    
    def do_get_sweep_time_auto(self):
        '''
        Reads the status the sweep time auto mode
            Output:
                auto enabled (int) : OFF = 0, ON = 1
        '''
        logging.info(__name__ + ' Reading sweep time auto state')
        return self._visainstrument.ask('SWE:TIME:AUTO?')
    def do_set_sweep_time_auto(self, enable):
        '''
        Sets the sweep time auto mode
            Input: 
                enable (int) : OFF = 0, ON = 1
        '''
        logging.info(__name__ + ' Setting the sweep time auto mode %s' %enable)
        self._visainstrument.write('SWE:TIME:AUTO %s' %enable)
    def do_get_sweep_time_auto_rules(self):
        '''
        Reads the rules for the auto sweep function
            Output:
                rule (string)
        '''
        logging.info(__name__ + ' Reading the sweep auto rules')
        return self._visainstrument.ask('SWE:TIME:AUTO:RUL?')
    def do_set_sweep_time_auto_rules(self, rule):
        '''
        Sets the rule for the sweep auto time
            Input (string):
                rule (string):
                    ['norm', 'normal', 'accuracy', 'acc', 'sres', 'sresponse']
        '''
        logging.info(__name__ + ' Setting the sweep time auto rule to %s'
                    %rule)
        self._visainstrument('SWE:TIME:AUTO:RUL %s' %rule)
    
    def get_all(self):
        '''
        Reads the status of all parameters
        '''
        logging.info(__name__ + ' Reading all parameter')
        self.get_frequency_center()
        self.get_frequency_start()
        self.get_frequency_stop()
        self.get_frequency_span()
        self.get_bandwidth_res()
        self.get_bandwidth_res_auto()
        self.get_bandwidth_video()
        self.get_bandwidth_video_auto()
        self.get_trigger_source()
        self.get_sweep_time()
        self.get_sweep_time_auto()
        self.get_sweep_time_auto_rules()
        self.get_continous_measurement()
        self.get_trace_1()
        self.get_trace_2()
        self.get_trace_3()
        self.get_trace_4()
        self.get_trace_5()
        self.get_trace_6()
    
    def reset(self):
        '''
        Resets the device to default state
        '''
        logging.info(__name__ + ' : resetting the device')
        self._visainstrument.write('*RST')
    def send_command(self, command):
        '''
        Sends a command to the instrument
            Input:
                command (string) : command to be sent (see manual for commands)
        '''
        self._visainstrument.write(command)
    def retrieve_data(self, query):
        '''
        Reads data from the instrument
            Input:
                query (string) : command to be sent (see manual for commands)
            Output:
                varies depending on command sent
        '''
        return self._visainstrument.ask(query)
        
    def is_valid_channel(self, channel):
        min_chan_val = 1
        max_chan_val = 6
        if channel < min_chan_val or channel > max_chan_val:
            raise ValueError('channel must be between {} and {}'.format(min_chan_val, max_chan_val))
        else:
            return channel
