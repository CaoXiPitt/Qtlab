# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 16:46:21 2015

@author: HatLab_Xi Cao
"""

#Aglient_MXA_N9020A

from instrument import Instrument
import visa
import types
import logging
import numpy as np

class Aglient_MXA_N9020A(Instrument):
    '''
    This is the driver for the Aglient MXA N9020A signal analyzer
    '''
    
    
    def __init__(self, name, address, reset=False):
        '''
        Initializes the Agilent_E5071C, and communicates with the wrapper.

        Input:
          name (string)    : name of the instrument
          address (string) : GPIB address
          reset (bool)     : resets to default values, default=False
        '''
        logging.info(__name__ + ' : Initializing instrument Agilent_E5071C')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        
        
        self.add_parameter('mode',flags=Instrument.FLAG_GETSET, type=types.StringType)
        #self.add_parameter('peak_threshold',flags=Instrument.FLAG_GETSET,units='dBm',type=types.FloatType)        
        
        
        self.add_function('marker_Y_value')
        self.add_function('new_peak')
        self.add_function('next_peak')
        self.add_function('next_peak_right')
        self.add_function('next_peak_left')
        self.add_function('marker_X_value')
        self.add_function('marker_off')
        
        if (reset):
            self.reset()
        else:
            self.get_all()
            
            
    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : resetting instrument')
        self._visainstrument.write('*RST')
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
        self.get_mode()
        #self.get_peak_threshold()
    
    #function:
    
    def marker_Y_value(self,markernum=1):
        '''
        Get the Y value for the No. markernum marker
        '''
        logging.info(__name__ + ' : get Y value of %i marker' % markernum)
        return float(self._visainstrument.ask(':CALCULATE:SPECTRUM:MARKER%i:Y? ' % markernum)) 

    def marker_X_value(self,markernum=1):
        '''
        Get the Y value for the No. markernum marker
        '''
        logging.info(__name__ + ' : get X value of %i marker' % markernum)
        return float(self._visainstrument.ask(':CALCULATE:SPECTRUM:MARKER%i:X? ' % markernum)) 

    def new_peak(self,markernum=1):
        '''
        Set the chosen marker on a peak
        '''
        logging.info(__name__ + ' : set the %i marker on a peak' % markernum)
        self._visainstrument.write(':CALCULATE:SPECTRUM:MARKER%i:MAXIMUM' % markernum)
        
    def next_peak(self,markernum=1):
        '''
        Set the chosen marker to the next peak
        '''
        logging.info(__name__ + ' : set the %i marker to the next peak' % markernum)
        self._visainstrument.write(':CALCULATE:SPECTRUM:MARKER%i:MAXIMUM:NEXT' % markernum)
        
    def next_peak_right(self,markernum=1):
        '''
        Set the chosen marker to the next peak right
        '''
        logging.info(__name__ + ' : set the %i marker to the next peak right' % markernum)
        self._visainstrument.write(':CALCULATE:SPECTRUM:MARKER%i:MAXIMUM:RIGHT' % markernum)    
    
    def next_peak_left(self,markernum=1):
        '''
        Set the chosen marker to the next peak
        '''
        logging.info(__name__ + ' : set the %i marker to the next peak left' % markernum)
        self._visainstrument.write(':CALCULATE:SPECTRUM:MARKER%i:MAXIMUM:LEFT' % markernum) 
        
    def marker_off(self,markernum=1):
        '''
        Turn off the chosen marker
        '''
        logging.info(__name__ + ' : turn off the %i marker' % markernum)
        self._visainstrument.write(':CALCULATE:SPECTRUM:MARKER%i:FUCTION OFF' % markernum)
        
        
    #parameter:
                
    def do_get_mode(self):
        '''
        Read the current mode of the instrument        
        
        '''
        logging.debug(__name__ + ' : get mode')
        return str(self._visainstrument.ask(':INSTRUMENT?'))   


    def do_set_mode(self,modename):             
        '''
        Set the mode of the instrument
        '''
        logging.debug(__name__ + ' : set mode to %s' % modename)
        self._visainstrument.write(':INSTRUMENT %s' % modename)        
        
        
    def do_get_peak_threshold(self):
        '''
        Get the peak threshold of the instrument 
        '''
        logging.debug(__name__ + ' : get the peak threshold of the instrument')
        return float(self._visainstrument.ask(':CALCULATE:SPECTRUM:MARKER:PEAK:THRESHOLD?'))
        
    def do_set_peak_threshold(self,threshold):
        '''
        Set the peak threshold of the instrument to "threshold" value
        
        This command will turn the peak threshold and peak threshold line functions at the same time
        '''
        logging.debug(__name__ + ' : set the peak threshold of the instrument to %f' % threshold)
        self._visainstrument.write(':CALCULATE:SPECTRUM:MARKER:PEAK:THRESHOLD %f' % threshold)


        
        