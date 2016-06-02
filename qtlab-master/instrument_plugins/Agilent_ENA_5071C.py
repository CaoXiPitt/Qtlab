# MJH 2015_10_15.. Maybe this will work??
#
from instrument import Instrument
import visa
import types
import logging
import numpy as np

class Agilent_ENA_5071C(Instrument):
    '''
    This is the driver for the Agilent E5071C Vector Netowrk Analyzer

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'Agilent_E5071C', address='<GBIP address>, reset=<bool>')
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

        self.add_parameter('power',
            flags=Instrument.FLAG_GETSET, units='dBm', minval=-80, maxval=10, type=types.FloatType)
        self.add_parameter('rfout',
            flags=Instrument.FLAG_GETSET, minval=0, maxval=1, type=types.IntType)
        self.add_parameter('nfpts', 
            flags=Instrument.FLAG_GETSET,minval=2, maxval=1601, type=types.IntType)
        self.add_parameter('sparam',
            flags=Instrument.FLAG_GETSET, type=types.StringType)
        self.add_parameter('fstart', 
            flags=Instrument.FLAG_GETSET, units='Hz', minval=300E3, maxval=20E9, type=types.FloatType)
        self.add_parameter('fstop', 
            flags=Instrument.FLAG_GETSET, units='Hz', minval=300E3, maxval=20E9, type=types.FloatType)
        self.add_parameter('ifbw', 
            flags=Instrument.FLAG_GETSET, units='Hz', minval=10, maxval=1500000, type=types.FloatType)
        self.add_parameter('avgstat', 
            flags=Instrument.FLAG_GETSET, minval=0, maxval=1, type=types.IntType)
        self.add_parameter('avgnum', 
            flags=Instrument.FLAG_GETSET, minval=1, maxval=999, type=types.IntType)
        self.add_parameter('trform',
            flags=Instrument.FLAG_GETSET, type=types.StringType)        
        
        self.add_function('reset')
        self.add_function ('get_all')
        self.add_function('getfdata')
        self.add_function('gettrace')
        self.add_function('trigger')
        

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
        self.get_power()
        self.get_rfout()
        self.get_nfpts()
        self.get_sparam()
        self.get_fstart()
        self.get_fstop()
        self.get_ifbw()
        self.get_avgstat()
        self.get_avgnum()
        self.get_trform()
    
    def trigger(self,ch):
        logging.info(__name__ + ' : trigger')
        self._visainstrument.write(":INIT%s" % ch)
    
    def getfdata(self):
        '''
        Gets freq stimulus data, returns array
        
        Input:
            None
        Output:
            freqvalues array (Hz)
        '''
        logging.info(__name__ + ' : get f stim data')
        strdata= str(self._visainstrument.ask(':SENS1:FREQ:DATA?'))
        return np.array(map(float,strdata.split(',')))
        
    def gettrace(self):
        '''
        Gets amp/phase stimulus data, returns 2 arrays
        
        Input:
            None
        Output:
            mags (dB) phases (rad)
        '''
        logging.info(__name__ + ' : get amp, phase stim data')
        strdata= str(self._visainstrument.ask(':CALC:DATA:FDATa?'))
        data= np.array(map(float,strdata.split(',')))
        data=data.reshape((len(data)/2,2))
        return data.transpose() # mags, phase
        
        
    def do_get_power(self):
        '''
        Reads the power of the signal from the instrument

        Input:
            None

        Output:
            Power of Source 1 (dBM)
        '''
        logging.debug(__name__ + ' : get power')
        return float(self._visainstrument.ask(':SOUR1:POW?'))

    def do_set_power(self, amp):
        '''
        Set the power of the signal

        Input:
            amp (float) : power in ?? (dBm)

        Output:
            None
        '''
        logging.debug(__name__ + ' : set power to %f' % amp)
        self._visainstrument.write(':SOUR1:POW %s' % amp)
    
    def do_get_rfout(self):
        '''
        Reads the rf output status from instrument
        
        Input:
            None
            
        Output
            RF output status (On/1, Off/0)
        '''
        logging.debug(__name__ + ': get status')
        return int(self._visainstrument.ask(':OUTP?'))
    
    def do_set_rfout(self, newout):
        '''
        Set the rf output status to On/1 Off/0
        
        Input: 
            New Output stat (1,0)
            
        Output:
            None
        '''
        logging.debug(__name__ + ' : set output status to %s' % newout)
        self._visainstrument.write(':OUTP %s' % newout )
    
    def do_get_nfpts(self):
        '''
        Get number of pts. in freq sweetp (int)
        
        Input: 
            None
            
        Outpt:
            Int # of freq pts 
        '''
        logging.debug(__name__ + ': get nfpts')
        return int(self._visainstrument.ask(':SENS1:SWE:POIN?')) 
    
    def do_set_nfpts(self, nfpts):
        '''
        set number of pts. in freq sweetp (int)
        
        Input: 
            None
            
        Outpt:
            Int # of freq pts 
        '''
        logging.debug(__name__ + ': set nfpts to %s' % nfpts)
        self._visainstrument.write(':SENS1:SWE:POIN %s' % nfpts)
        
    def do_get_sparam(self):
        '''
        Get Sparam of current msmt 
        
        Input: 
            None
            
        Outpt:
            Sxx as string 
        '''
        logging.debug(__name__ + ': get sparam')
        return str(self._visainstrument.ask(':CALC1:PAR1:DEF?')) 
    
    def do_set_sparam(self, sparam):
        '''
        Set Sparam of current msmt
        
        Input: 
            New Sparam in form Sxx (string)
            
        Outpt:
             None
        '''
        logging.debug(__name__ + ': set sparam to %s' % sparam)
        self._visainstrument.write(':CALC1:PAR1:DEF %s' % sparam)
    def do_get_fstart(self):
        '''
        Get start freq
        
        Input: 
            None
            
        Outpt:
            start freq (Hz) 
        '''
        logging.debug(__name__ + ': get fstart')
        return float(self._visainstrument.ask(':SENS1:FREQ:STAR?')) 
    
    def do_set_fstart(self, fstart):
        '''
        Set start freq
        
        Input: 
            start freq (Hz)
            
        Outpt:
            None
        '''
        logging.debug(__name__ + ': set fstart to %s' % fstart)
        self._visainstrument.write(':SENS1:FREQ:STAR %s' % fstart)
    def do_get_fstop(self):
        '''
        Get stop freq
        
        Input: 
            None
            
        Outpt:
            stop freq (Hz) 
        '''
        logging.debug(__name__ + ': get fstop')
        return float(self._visainstrument.ask(':SENS1:FREQ:STOP?')) 
    
    def do_set_fstop(self, fstop):
        '''
        Set stop freq
        
        Input: 
            stop freq (Hz) 
            
        Outpt:
            None 
        '''
        logging.debug(__name__ + ': set fstop to %s' % fstop)
        self._visainstrument.write(':SENS1:FREQ:STOP %s' % fstop)
    def do_get_ifbw(self):
        '''
        Get ifbw 
        
        Input: 
            None
            
        Outpt:
            ifbw (Hz) 
        '''
        logging.debug(__name__ + ': get ifbw')
        return float(self._visainstrument.ask(':SENS1:BWID?')) 
    
    def do_set_ifbw(self, ifbw):
        '''
        Set ifbw
        
        Input: 
            ifbw (Hz) 
            
        Outpt:
            None 
        '''
        logging.debug(__name__ + ': set ifbw to %s' % ifbw)
        self._visainstrument.write(':SENS1:BWID %s' % ifbw)
    def do_get_avgstat(self):
        '''
        Get avgstatus (1/On 0/off) 
        
        Input: 
            None
            
        Outpt:
            avgstatus (1/On 0/off) 
        '''
        logging.debug(__name__ + ': get avgstat')
        return int(self._visainstrument.ask(':SENS1:AVER?')) 
    
    def do_set_avgstat(self, avgstat):
        '''
        Set average status (1/On 0/off)
        
        Input: 
            new avgstat (1/0)
            
        Outpt:
            None 
        '''
        logging.debug(__name__ + ': set ifbw to %s' % avgstat)
        self._visainstrument.write(':SENS1:AVER %s' % avgstat)
    def do_get_avgnum(self):
        '''
        Get avg num
        
        Input: 
            None
            
        Outpt:
            avg num
        '''
        logging.debug(__name__ + ': get avgsnum')
        return int(self._visainstrument.ask(':SENS1:AVER:COUN?')) 
    
    def do_set_avgnum(self, avgnum):
        '''
        Set average number
        
        Input: 
            new avg number
            
        Outpt:
            None 
        '''
        logging.debug(__name__ + ': set avg # to %s' % avgnum)
        self._visainstrument.write(':SENS1:AVER:COUN %s' % avgnum)
    def do_get_trform(self):
        '''
        Get trace format
        
        Input: 
            None
            
        Outpt:
            trace format (string)
        '''
        logging.debug(__name__ + ': get format')
        return str(self._visainstrument.ask(':CALC1:FORM?')) 
    
    def do_set_trform(self, f):
        '''
        Set trace format
        
        Input: 
            new format (string)
          
        Outpt:
            None 
        '''
        logging.debug(__name__ + ': set trace  format to %s' % f)
        self._visainstrument.write(':CALC1:FORM %s' % f)    
        
        
        
        
    # shortcuts
    def off(self):
        '''
        Set status to 'off'

        Input:
            None

        Output:
            None
        '''
        logging.debug(__name__ + ' : set output OFF')
        self._visainstrument.write(':OUTP:STAT OFF')

    def on(self):
        '''
        Set status to 'off'

        Input:
            None

        Output:
            None
        '''
        logging.debug(__name__ + ' : set output ON')
        self._visainstrument.write(':OUTP:STAT ON')
    
