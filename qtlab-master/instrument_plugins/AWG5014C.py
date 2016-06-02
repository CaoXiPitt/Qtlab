# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 14:18:43 2015

@author: HatLab_Xi Cao
"""

from instrument import Instrument
import visa
import types
import logging
import numpy as np
import struct


class AWG5014C (Instrument):
    '''
    This is the driver for the Agilent E5071C Vector Netowrk Analyzer

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'AWG5014C', address='<GBIP address>, reset=<bool>')
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the AWG5014C, and communicates with the wrapper.

        Input:
          name (string)    : name of the instrument
          address (string) : GPIB address
          reset (bool)     : resets to default values, default=False
        '''
        logging.info(__name__ + ' : Initializing instrument AWG5014C')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        
        #self.add_parameter('runningstate',flags=Instrument.FLAG_GETSET, type=types.BooleanType)
        self.add_parameter('DC1output',flags=Instrument.FLAG_GETSET, type=types.IntType)
        #self.add_parameter('sequence',flags=Instrument.FLAG_GETSET, type=types.StringType)     
        self.add_parameter('AWGmode',flags=Instrument.FLAG_GETSET, type=types.StringType)
        self.add_parameter('sequence_length',flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('internal_trigger_rate',flags=Instrument.FLAG_GETSET, type=types.FloatType)
        self.add_parameter('ch1offset',flags=Instrument.FLAG_GETSET,units='V', type=types.FloatType)
        self.add_parameter('ch2offset',flags=Instrument.FLAG_GETSET,units='V', type=types.FloatType)
        self.add_parameter('ch3offset',flags=Instrument.FLAG_GETSET,units='V', type=types.FloatType)
        self.add_parameter('ch4offset',flags=Instrument.FLAG_GETSET,units='V', type=types.FloatType)
        self.add_parameter('ch1skew',flags=Instrument.FLAG_GETSET,units='s', type=types.FloatType)
        self.add_parameter('ch2skew',flags=Instrument.FLAG_GETSET,units='s', type=types.FloatType)
        self.add_parameter('ch3skew',flags=Instrument.FLAG_GETSET,units='s', type=types.FloatType)
        self.add_parameter('ch4skew',flags=Instrument.FLAG_GETSET,units='s', type=types.FloatType)
        self.add_parameter('ch1amp',flags=Instrument.FLAG_GETSET,units='V', type=types.FloatType)
        self.add_parameter('ch2amp',flags=Instrument.FLAG_GETSET,units='V', type=types.FloatType)
        self.add_parameter('ch3amp',flags=Instrument.FLAG_GETSET,units='V', type=types.FloatType)
        self.add_parameter('ch4amp',flags=Instrument.FLAG_GETSET,units='V', type=types.FloatType)
        
        self.add_function('get_all')
        self.add_function('newwaveform')
        self.add_function('setwaveform')
        self.add_function('waittrigger')
        self.add_function('addwaveform')
        self.add_function('run')
        self.add_function('stop')
        self.add_function('force_trigger')
        self.add_function('setloop')
        self.add_function('deletewaveform')
        self.add_function('set_ch_offset')
        self.add_function('addwaveform_nonseq')
        self.add_function('channel_on')
        self.add_function('channel_off')
        self.add_function('goto_state')
        self.add_function('goto_index')
        self.add_function('addmarker')
        self.add_function('deleteall')
        
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
        
        self.get_DC1output()
        self.get_AWGmode()   
        self.get_ch1offset()
        self.get_ch2offset()
        self.get_ch3offset()
        self.get_ch4offset()
        self.get_ch1skew()
        self.get_ch2skew()
        self.get_ch3skew()
        self.get_ch4skew()
        self.get_ch1amp()
        self.get_ch2amp()
        self.get_ch3amp()
        self.get_ch4amp()
        self.get_internal_trigger_rate()
        self.get_sequence_length()
        
    def newwaveform(self,waveformname):
        '''
        create a new blank waveform in the waveform list.
        
        Input: a string with form '"waveformname",number of the point in the waveform, waveform type(integer or real)'
        e.g. '"TEST", 1024, INTEGER'
        '''
        logging.info(__name__ + ' : create a new wave form')
        self._visainstrument.write('WLIST:WAVEFORM:NEW %s' % waveformname)
        
    def setwaveform(self,wavestr):
        '''
        set value for a waveform that is in the waveform list (if waveform is not existed, use newwaveform to create one)
    
        '''
        logging.info(__name__ + ' : set value for a waveform')
        self._visainstrument.write('WLIST:WAVEFORM:DATA %s' % wavestr)
        
    def addwaveform(self,element,channel,wavename):
        '''
        Add waveform called "wavename" to the sequence and its position is given by channel and element
        '''
        logging.info(__name__ + ' : add a waveform to "channel"th channel of "element"th element')
        commandstr = 'SEQUENCE:ELEMENT%i:' % element + 'WAVEFORM%i' % channel + ' "%s"' % wavename
        self._visainstrument.write(commandstr)
        
    def addwaveform_nonseq(self,channel,wavename):
        '''
        Add waveform called "wavename" to the channel
        '''
        logging.info(__name__ + ' : add waveform %s' % wavename + ' to %i channel' % channel)
        self._visainstrument.write('SOURCE%i' % channel +':WAVEFORM "%s"' % wavename)
        
        
    def setmode(self,awgmode):
        '''
        Set AWG runmode 
        '''
        logging.info(__name__ + ' : select mode for AWG5014C')
        self._visainstrument.write('AWGCONTROL:RMODE %s' % awgmode)
    
                     
    def waittrigger(self,element,command):
        '''
        Set or ask the wait trigger state of a certain element in the sequence
        Input: element number (int), command (0: no wait, 1: wait, 3: check the state)
        '''
        
        logging.info(__name__ + ': get wait trigger state')
        
        if (int(command) == 0):
            self._visainstrument.write('SEQUENCE:ELEMENT%i:TWAIT 0' % element)
  
        elif (int(command) == 1):
            self._visainstrument.write('SEQUENCE:ELEMENT%i:TWAIT 1' % element)
            
        #state = self._visainstrument.ask('SEQUENCE:ELEMENT%i:TWAIT?' % element)
        #print 'The wait trigger state for the desired element is:(0 for no wait, 1 for wait)'
        #print state
            
    def run(self):
        '''
        Run AWG
        '''        
        logging.info(__name__ + ' : run the AWG')
        self._visainstrument.write('AWGCONTROL:RUN')     
        
    def stop(self):
        '''
        Stop AWG
        '''
        logging.info(__name__ + ' : stop the AWG')
        self._visainstrument.write('AWGCONTROL:STOP')
        
    def channel_on(self,channel_num):
        '''
        Turn on the chosen channel
        '''
        logging.info(__name__ + ' : turn on the %ith channel' % channel_num)
        self._visainstrument.write('OUTPUT%i:STATE ON' % channel_num)

    def channel_off(self,channel_num):
        '''
        Turn off the chosen channel
        '''
        logging.info(__name__ + ' : turn off the %ith channel' % channel_num)
        self._visainstrument.write('OUTPUT%i:STATE OFF' % channel_num)
        
        
    def force_trigger(self):
        '''
        Make a force trigger
        '''
        logging.info(__name__ + ' : make a force trigger')
        self._visainstrument.write('TRIGGER:SEQUENCE:IMMEDIATE')
        
        
    def setloop(self,channelnum,looptimes):
        '''
        Set the loop times for channle channelnum
        '''
        logging.info(__name__ + ' : set loop times for some certain channel')
        self._visainstrument.write('SEQUENCE:ELEMENT%i' % channelnum + ':LOOP:COUNT %i' % looptimes)
        
    def deletewaveform(self,wavename):
        '''
        delete a waveform in the waveform list
        '''        
        logging.info(__name__ + ' : delete a waveform with the name: %s' % wavename)
        self._visainstrument.write('WLIST:WAVEFORM:DELETE "%s"' % wavename)
        
        
    def set_ch_offset(self,ch_num,offset):
        '''
        Get the offset of a channle
        '''
        logging.info(__name__ + ' : get the offset of %ith channle' % ch_num + ' to %f' % offset)
        self._visainstrument.write('SOURCE%i' % ch_num + ':VOLTAGE:LEVEL:IMMEDIATE:OFFSET %f' % offset)
        
    def goto_state(self,element,state):
        '''
        Set the goto state of the chosen element to be on of off
        '''
        logging.info(__name__ + ' : set the goto state of the %ith' % element + ' element to be %i' % state)
        self._visainstrument.write('SEQUENCE:ELEMENT%i' % element + ':GOTO:STATE %i' % state)
        
    def goto_index(self,element,index):
        '''
        Set the chosen element go to the desired index
        '''
        logging.info(__name__ + ' : set the %i' % element + ' go to index %i' % index)
        self._visainstrument.write('SEQUENCE:ELEMENT%i' % element + ' :GOTO:INDEX %i' % index)
        
    def addmarker(self,wavename,datastr):
        '''
        Add the marker to a waveform
        '''
        logging.info(__name__ + ' : add the marker to the waveform %s' % wavename)
        self._visainstrument.write('WLIST:WAVEFORM:MARKER:DATA %s' % datastr)
        
    def deleteall(self):
        '''
        Delete all user-defined waveforms
        '''        
        logging.info(__name__ + ' : delete all the user-defined waveforms')
        self._visainstrument.write('WLIST:WAVEFORM:DELETE ALL')
    
    #parameter        
 
        
        
    def do_set_DC1output(self, amp):
        logging.debug(__name__ + ' : set DC1output to %s' % amp)
        self._visainstrument.write('AWGControl:DC1:STATe %s' % amp)
        
        
        
        
    def do_get_DC1output(self):
        logging.debug(__name__+' : get DC1output')
        return int(self._visainstrument.ask('AWGControl:DC1:STATe?'))
        
        
    def do_set_sequence_length(self,wavelength):        
        logging.debug(__name__ + ' : create a new sequence')
        self._visainstrument.write('SEQUENCE:LENGTH %i' % wavelength)

        
        
    def do_get_sequence_length(self):
        logging.debug(__name__ + ' : get sequence length ')
        return str(self._visainstrument.ask('SEQUENCE:LENGTH?'))


    def do_set_AWGmode(self,awgmode):
        '''
        Set the mode for AWG
        Input: CONTIMUOUS, TRIGERED, GATED, SEQUENCE (string)
        Output: nothing
        '''
        logging.debug(__name__ + ' : set AWGmode ')
        self._visainstrument.write('AWGCONTROL:RMODE %s' % awgmode)
        
    def do_get_AWGmode(self):
        '''
        Get the mode for AWG
        Input: nothing
        Output: CONTIMUOUS, TRIGERED, GATED, SEQUENCE (string)
        '''
        logging.debug(__name__ + ' : get AWGmode ')
        return str(self._visainstrument.ask('AWGCONTROL:RMODE?'))
        
    def do_get_internal_trigger_rate(self):
        '''
        Get the internal trigger rate
        Input: nothing
        Output: trigger rate 
        '''
        logging.debug(__name__ + ' : get internal trigger rate ')
        return float(self._visainstrument.ask('TRIGGER:SEQUENCE:TIMER?'))
        
    def do_set_internal_trigger_rate(self,time):
        '''
        Set the internal trigger rate
        Input: trigger rate (float and in unit of second)
        '''
        logging.debug(__name__ + ' : set internal trigger rate ')
        commandstr = 'TRIGGER:SEQUENCE:TIMER %f' % time + 's'
        self._visainstrument.write(commandstr)
        
        
    def do_get_ch1offset(self):
        '''
        Get the DC offset of Channel 1
        Input: nothing
        Output: DC offset of Channel 1
        '''        
        logging.debug(__name__ + ' : get the DC offset of Channel 1')
        self._visainstrument.ask('SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:OFFSET?')
        return float(self._visainstrument.ask('SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:OFFSET?'))
    
    def do_set_ch1offset(self,voltage):
        '''
        Set the DC offset of Channel 1
        Input: the offset voltage in volt
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the DC offset of Channel 1 to %f' % voltage)
        self._visainstrument.write('SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:OFFSET %f' % voltage)
        

    def do_get_ch2offset(self):
        '''
        Get the DC offset of Channel 2
        Input: nothing
        Output: DC offset of Channel 2
        '''        
        logging.debug(__name__ + ' : get the DC offset of Channel 2')
        self._visainstrument.ask('SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:OFFSET?')
        return float(self._visainstrument.ask('SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:OFFSET?'))
    
    def do_set_ch2offset(self,voltage):
        '''
        Set the DC offset of Channel 2
        Input: the offset voltage in volt
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the DC offset of Channel 2 to %f' % voltage)
        self._visainstrument.write('SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:OFFSET %f' % voltage)
        
    def do_get_ch3offset(self):
        '''
        Get the DC offset of Channel 3
        Input: nothing
        Output: DC offset of Channel 3
        '''        
        logging.debug(__name__ + ' : get the DC offset of Channel 3')
        self._visainstrument.ask('SOURCE3:VOLTAGE:LEVEL:IMMEDIATE:OFFSET?')
        return float(self._visainstrument.ask('SOURCE3:VOLTAGE:LEVEL:IMMEDIATE:OFFSET?'))
    
    def do_set_ch3offset(self,voltage):
        '''
        Set the DC offset of Channel 3
        Input: the offset voltage in volt
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the DC offset of Channel 3 to %f' % voltage)
        self._visainstrument.write('SOURCE3:VOLTAGE:LEVEL:IMMEDIATE:OFFSET %f' % voltage)

    def do_get_ch4offset(self):
        '''
        Get the DC offset of Channel 4
        Input: nothing
        Output: DC offset of Channel 4
        '''        
        logging.debug(__name__ + ' : get the DC offset of Channel 4')
        self._visainstrument.ask('SOURCE4:VOLTAGE:LEVEL:IMMEDIATE:OFFSET?')
        return float(self._visainstrument.ask('SOURCE4:VOLTAGE:LEVEL:IMMEDIATE:OFFSET?'))
    
    def do_set_ch4offset(self,voltage):
        '''
        Set the DC offset of Channel 4
        Input: the offset voltage in volt
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the DC offset of Channel 4 to %f' % voltage)
        self._visainstrument.write('SOURCE4:VOLTAGE:LEVEL:IMMEDIATE:OFFSET %f' % voltage)

    def do_get_ch1skew(self):
        '''
        Get the skew time of Channel 1
        Input: nothing
        Output: Skew time of Channel 1 in second
        '''        
        logging.debug(__name__ + ' : get the skew time of Channel 1')
        self._visainstrument.ask('SOURCE1:SKEW?')
        return float(self._visainstrument.ask('SOURCE1:SKEW?'))
    
    def do_set_ch1skew(self,skewtime):
        '''
        Set the skew time of Channel 1
        Input: the skew time in nanosecond
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the skew time of Channel 1 to %f' % skewtime + ' nanosecond')
        self._visainstrument.write('SOURCE1:SKEW %f' % skewtime + 'NS')
        
    def do_get_ch2skew(self):
        '''
        Get the skew time of Channel 2
        Input: nothing
        Output: Skew time of Channel 2 in second
        '''        
        logging.debug(__name__ + ' : get the skew time of Channel 2')
        self._visainstrument.ask('SOURCE2:SKEW?')
        return float(self._visainstrument.ask('SOURCE2:SKEW?'))
    
    def do_set_ch2skew(self,skewtime):
        '''
        Set the skew time of Channel 2
        Input: the skew time in nanosecond
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the skew time of Channel 2 to %f' % skewtime + ' nanosecond')
        self._visainstrument.write('SOURCE2:SKEW %f' % skewtime + 'NS')    
        
    def do_get_ch3skew(self):
        '''
        Get the skew time of Channel 3
        Input: nothing
        Output: Skew time of Channel 3 in second
        '''        
        logging.debug(__name__ + ' : get the skew time of Channel 3')
        self._visainstrument.ask('SOURCE3:SKEW?')
        return float(self._visainstrument.ask('SOURCE3:SKEW?'))
    
    def do_set_ch3skew(self,skewtime):
        '''
        Set the skew time of Channel 3
        Input: the skew time in nanosecond
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the skew time of Channel 3 to %f' % skewtime + ' nanosecond')
        self._visainstrument.write('SOURCE3:SKEW %f' % skewtime + 'NS')    
        
    def do_get_ch4skew(self):
        '''
        Get the skew time of Channel 4
        Input: nothing
        Output: Skew time of Channel 4 in second
        '''        
        logging.debug(__name__ + ' : get the skew time of Channel 4')
        self._visainstrument.ask('SOURCE4:SKEW?')
        return float(self._visainstrument.ask('SOURCE4:SKEW?'))
    
    def do_set_ch4skew(self,skewtime):
        '''
        Set the skew time of Channel 4
        Input: the skew time in nanosecond
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the skew time of Channel 4 to %f' % skewtime + ' nanosecond')
        self._visainstrument.write('SOURCE4:SKEW %f' % skewtime + 'NS')          
        
    def do_get_ch1amp(self):
        '''
        Get the amplitude of Channel 1
        Input: nothing
        Output: Amplitude of Channel 1 in volt
        '''        
        logging.debug(__name__ + ' : get the amplitude of Channel 1')
        self._visainstrument.ask('SOURCE1:VOLTAGE:AMPLITUDE?')
        return float(self._visainstrument.ask('SOURCE1:VOLTAGE:AMPLITUDE?'))
    
    def do_set_ch1amp(self,amplitude):
        '''
        Set the amplitude of Channel 1 in volt
        Input: The amplitude in volt
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the amplitude of Channel 1 to %f' % amplitude + ' volt')
        self._visainstrument.write('SOURCE1:VOLTAGE:AMPLITUDE %f' % amplitude)        
        
    def do_get_ch2amp(self):
        '''
        Get the amplitude of Channel 2
        Input: nothing
        Output: Amplitude of Channel 2 in volt
        '''        
        logging.debug(__name__ + ' : get the amplitude of Channel 2')
        self._visainstrument.ask('SOURCE2:VOLTAGE:AMPLITUDE?')
        return float(self._visainstrument.ask('SOURCE2:VOLTAGE:AMPLITUDE?'))
    
    def do_set_ch2amp(self,amplitude):
        '''
        Set the amplitude of Channel 2 in volt
        Input: The amplitude in volt
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the amplitude of Channel 2 to %f' % amplitude + ' volt')
        self._visainstrument.write('SOURCE2:VOLTAGE:AMPLITUDE %f' % amplitude)        

    def do_get_ch3amp(self):
        '''
        Get the amplitude of Channel 3
        Input: nothing
        Output: Amplitude of Channel 3 in volt
        '''        
        logging.debug(__name__ + ' : get the amplitude of Channel 3')
        self._visainstrument.ask('SOURCE3:VOLTAGE:AMPLITUDE?')
        return float(self._visainstrument.ask('SOURCE3:VOLTAGE:AMPLITUDE?'))
    
    def do_set_ch3amp(self,amplitude):
        '''
        Set the amplitude of Channel 3 in volt
        Input: The amplitude in volt
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the amplitude of Channel 3 to %f' % amplitude + ' volt')
        self._visainstrument.write('SOURCE3:VOLTAGE:AMPLITUDE %f' % amplitude)         


    def do_get_ch4amp(self):
        '''
        Get the amplitude of Channel 4
        Input: nothing
        Output: Amplitude of Channel 4 in volt
        '''        
        logging.debug(__name__ + ' : get the amplitude of Channel 4')
        self._visainstrument.ask('SOURCE4:VOLTAGE:AMPLITUDE?')
        return float(self._visainstrument.ask('SOURCE4:VOLTAGE:AMPLITUDE?'))
    
    def do_set_ch4amp(self,amplitude):
        '''
        Set the amplitude of Channel 4 in volt
        Input: The amplitude in volt
        Output: Nothing
        '''
        logging.debug(__name__ + ' : set the amplitude of Channel 4 to %f' % amplitude + ' volt')
        self._visainstrument.write('SOURCE4:VOLTAGE:AMPLITUDE %f' % amplitude)         
        

        
'''           
    def do_get_runningstate(self):

        Reads the power of the signal from the instrument

        Input:
            None

        Output:
            Power of Source 1 (dBM)

        logging.debug(__name__ + ' : get runningstate')
        return bool(self._visainstrument.ask('AWGControl:APPLication:STATe?"SERIALXPRESS"'))      
'''         
        
        
        
        
        
        