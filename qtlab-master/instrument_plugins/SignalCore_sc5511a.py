
import usb1
import types
import logging
#import SC5511A_CONSTANTS as constant
from struct import pack, unpack
from math import floor
from instrument import Instrument

    
class SignalCore_sc5511a(Instrument):       
    OFF = 0x00
    ON = 0x01
    
    def __init__(self, name, serial_number=None):
        Instrument.__init__(self, name, tags=['generate'])
        self._serial_number = serial_number
        self._handle = None
        # Methods supported by both Signal Generators
        self.add_parameter('output_status', type = types.StringType,
                           flags = Instrument.FLAG_GETSET)
        self.add_parameter('frequency', type = types.FloatType,
                           flags=Instrument.FLAG_GETSET, units = ' Hz')
        self.add_parameter('reference_source', type = types.IntType,
                           flags = Instrument.FLAG_GET, options_list = [0, 1])
        self.add_parameter('alc_auto', type = types.IntType,
                           flags = Instrument.FLAG_GET, options_list = [0, 1])
        
        
        self.add_parameter('temperature', type=types.FloatType,
                           flags=Instrument.FLAG_GET, units= u'\N{DEGREE CELSIUS}')
        self.reg_write(constant.REFERENCE_MODE, [SignalCore_sc5511a.ON])
        self.reg_write(constant.RF2_STANDBY, [SignalCore_sc5511a.ON])
        self.add_function('search_devices')
        self.add_function('open_device')
        self.add_function('close_device')
        self.add_function('get_rf_parameters')
        self.add_function('get_device_status')
        self.add_function('get_device_info')
        self.add_function('get_alc_dac')
        self.add_function('set_frequency')
        self.add_function('set_synth_mode')
        self.add_function('set_rf_mode')
        self.add_function('set_power_level')
        self.add_function('set_output')
        self.add_function('set_alc_mode')
        self.add_function('set_standby')
        self.add_function('set_clock_reference')
        self.add_function('set_reference_dac')
        self.add_function('set_alc_dac')
        self.add_function('set_rf2_frequency')
        self.add_function('set_rf2_standby')
        self.add_function('list_mode_config')
        self.add_function('list_start_freq')
        self.add_function('list_stop_freq')
        self.add_function('list_step_freq')
        self.add_function('list_dwell_time')
        self.add_function('list_cycle_count')
        self.add_function('list_buffer_points')
        self.add_function('list_buffer_write')
        self.add_function('list_buffer_transfer')
        self.add_function('list_soft_trigger')
        self.add_function('list_buffer_read')
        self.add_function('auto_level_disable')
        self.add_function('store_default_state')
        self.add_function('synth_self_cal')

## QtLab Methods      
    def do_get_output_status(self):
        '''
        Reads the output status of RF1
            Output:
                status (int) : OFF = 0 ; ON = 1
        '''
        status = self.reg_read(constant.GET_DEVICE_STATUS, [0x00])      
        return _invert((status >> 12) & 0x01)#inverted for uniformity
    def do_set_output_status(self, enable):
        """
        Turns the output of RF1 on or off.
            Input: 
                enable (int) = OFF = 0 ; ON = 1
        """
        self.reg_write(constant.RF_STANDBY, [_invert(enable)])#inverted for uniformity

    def do_get_frequency(self):
        '''
        Reads the frequency of RF1
            Output:
                frequency (int) : in Hz
        '''
        logging.info(__name__ + ' : getting RF1 frequency')
        return self.reg_read(constant.GET_RF_PARAMETERS, [0x00])
    def do_set_frequency(self, frequency):
        """
        Sets RF1 frequency. Valid between 100MHz and 20GHz
            Args:
                frequency (int) = frequency in Hz
        """
        if (frequency >= 100000000 and frequency <= 20000000000):
            return self.reg_write(constant.RF_FREQUENCY, _to_bytearray(frequency))
        else:
            return constant.INPUTOUTOFRANGE
            
    def do_get_reference_source(self):
        '''
        Reads the state of external reference source
            Output: 
                state (int) : OFF = 0 ; ON = 1
        '''
        logging.info(__name__ + ' : getting reference state')
        status = self.reg_read(constant.GET_DEVICE_STATUS, [0x00])
        return (status >> 16) & 0x01
    def do_set_reference_source(self, enable):
        '''
        Sets whether an external reference source is used
            Input:
                enable (int) : OFF = 0; ON = 1
        '''
        return self.reg_write(constant.REFERENCE_MODE, [enable])
    def do_get_alc_auto(self):
        '''
        Reads the state of ALC
            Output: 
                state (int) : OFF = 0 ; ON = 1  
        '''
        return _invert((self.reg_read(constant.AUTO_LEVEL_DISABLE,[0x00]) >> 13) & 0x01)#inverted for uniformity
    def do_set_alc_auto(self, enable):
        '''
        Sets whether Auto Leveling is enabled
            Input:
                state (int) : OFF = 0 ; ON = 1
        '''
        self.reg_write(constant.AUTO_LEVEL_DISABLE, [_invert(enable)])#inverted for uniformity
        
    def do_get_temperature(self):
        """
        Returns temperature of device
            Output:
                temperature (float) : in Celsius?
        """
        logging.info(__name__ + ' : getting temperature')
        temp = self.reg_read(constant.GET_TEMPERATURE,[0x00])
        return _to_float32(temp)

## device communication        
    def search_devices(self):
        context = usb1.USBContext()
        device_list = []
        for device in context.getDeviceList():
                if device.getVendorID() == constant.SCI_USB_VID and device.getProductID() == constant.SCI_USB_PID:
                    device_list.append(device.getSerialNumber())
        return device_list
        
    def open_device(self):
        context = usb1.USBContext()
        if self.serial_number is None:
            self._handle = context.openByVendorIDAndProductID(constant.SCI_USB_VID,
                                                    constant.SCI_USB_PID)
        else:
            devices = context.getDeviceList()
            for device in devices:
                if device.getVendorID() == constant.SCI_USB_VID and device.getProductID() == constant.SCI_USB_PID:
                   if device.getSerialNumber() == self.serial_number:
                       self._handle = device.open()
                       break
        if self._handle is not None:
            self._handle.resetDevice()
            self._handle.setConfiguration(1)
            self._handle.claimInterface(0)
            self.reg_write(constant.SET_SYS_ACTIVE, [0x01])
            
    def close_device(self):
        if self._handle is not None:
            self.reg_write(constant.SET_SYS_ACTIVE, [0x00])
            self._handle.releaseInterface(0)
            self._handle.close()
    
    def reg_write(self, register, instruction):
        """ Send instruction to Generator \n
            Input: register = int, instruction = list \n
            returns: number of bytes actually sent"""
        if register in constant.CONFIG_REGISTER_SIZES:
            command = bytearray([register]) + bytearray(instruction)
            if self._handle is not None:
                bytes_sent = self._handle.controlWrite(0x41, 0, 0, 0, command, 1)
                if bytes_sent > 0:
                    return constant.SUCCESS
                else:
                    return constant.USBDEVICEERROR
        else:
            return constant.INVALIDCOMMAND
            
    def reg_read(self, register, instruction):
        """ Read data from Generator  \n
             Input: register = int, instruction = list  \n
             Returns: data if successful. -11 otherwise"""
        if register in constant.QUERY_REGISTER_SIZES:
            size = constant.QUERY_REGISTER_SIZES.get(register)
            self.reg_write(register, instruction)
            return self._handle.controlRead(0x41, 0, 0, 0, size, 10)
        else:
            return constant.INVALIDCOMMAND
##--Getters----------------------------------------------------------------------------               
    def get_rf_parameters(self):
        """
        Gets the current RF parameters such as RF1 frequency, 
        RF2 frequency, and sweep start frequency, etc.
        """
        params = []
        # rf1 freq
        value = self.reg_read(constant.GET_RF_PARAMETERS, [0x00])
        params.append(constant.RF_PARAMETERS_TITLES[0] + ' %d' %value)
        # sweep start freq 
        value = self.reg_read(constant.GET_RF_PARAMETERS, [0x01])
        params.append(constant.RF_PARAMETERS_TITLES[1] + ' %d' %value)
        #sweep stop freq    
        value = self.reg_read(constant.GET_RF_PARAMETERS, [0x02])
        params.append(constant.RF_PARAMETERS_TITLES[2] + ' %d' %value)
        # sweep step freq
        value = self.reg_read(constant.GET_RF_PARAMETERS, [0x03])    
        params.append(constant.RF_PARAMETERS_TITLES[3] + ' %d' %value)
        # sweep dwell time 
        value = self.reg_read(constant.GET_RF_PARAMETERS, [0x04])>>8
        params.append(constant.RF_PARAMETERS_TITLES[4] + ' %d' %value)
        #sweep cycles
        value = self.reg_read(constant.GET_RF_PARAMETERS, [0x05])>>8        
        params.append(constant.RF_PARAMETERS_TITLES[5] + ' %d' %value)
        # list buffer points 
        value = self.reg_read(constant.GET_RF_PARAMETERS, [0x06])>>8
        params.append(constant.RF_PARAMETERS_TITLES[6] + ' %d' %value)
        # rf level
        value = _to_float32(self.reg_read(constant.GET_RF_PARAMETERS, [0x07])>>8)
        params.append(constant.RF_PARAMETERS_TITLES[7] + ' %f' %value)
        # rf2 freq 
        value = self.reg_read(constant.GET_RF_PARAMETERS, [0x08])>>24
        params.append(constant.RF_PARAMETERS_TITLES[8] + ' %d' %value)#in MHz
        return params
        
    def get_device_status(self):
        """
        Gets the current device status such as the PLL 
        lock status, sweep modes, and other operating conditions.
        """
        status = self.reg_read(constant.GET_DEVICE_STATUS, [0x00])
        s_status = []
        for i in range(len(constant.STATUS_TITLES)):
            bitshift = i
            if bitshift >= 22:
                bitshift += 2
            value = (status >> bitshift) & 0x01
            s_status.append('{} : {}\n'.format(constant.STATUS_TITLES[i], value))
        return s_status
        
       
    def get_device_info(self):
        """
        Obtains the device information such as serial number,
        hardware revision, firmware revision, and manufactured date.
        """
        info = []
        # product serial number
        value = self.reg_read(constant.GET_DEVICE_INFO, [0x00])
        info.append(constant.DEVICE_INFO_TITLES[0] + '%s' %value)
        # Hardware Revision Conversion
        value = self.reg_read(constant.GET_DEVICE_INFO, [0x01])
        value = _to_float32(value)
        info.append(constant.DEVICE_INFO_TITLES[1] + '%s' %value)
        # Firmware Revision Conversion
        value = self.reg_read(constant.GET_DEVICE_INFO, [0x02])
        value = _to_float32(value)
        info.append(constant.DEVICE_INFO_TITLES[2] + '%s' %value)
        # Manufacture Date
        date = self.reg_read(constant.GET_DEVICE_INFO, [0x03])
        info.append(constant.DEVICE_INFO_TITLES[3] + 
            ' {}/{}/{} {}'.format((date >> 16) & 0xFF, # month
                                  (date >> 8) & 0xFF, #day
                                  (date >> 24) & 0xFF,#year
                                  date & 0xFF)) #hour
        return info
        
    def get_alc_dac(self):
        """
        Retrieves the current value of the ALC DAC which set the 
        power level of channel RF1.
        """
        return self.reg_read(constant.GET_ALC_DAC_VALUE, [0x00])
        
#--Setters----------------------------------------------------------------------------            
           
    def set_synth_mode(self,lock_mode, loop_gain, disable_spur_suppression):
        """
        Sets synthesizer mode of RF1. (see manual for greater detail)
            Args:
                disable_spur_suppression (int)= set the spur suppression behavior
                loop_gain (int) = set synth loop gain
                lock_mode (int) = set lock mode of RF1
        """
        instruction = (disable_spur_suppression << 2| loop_gain << 1 | lock_mode)
        return self.reg_write(constant.SYNTH_MODE, [instruction])
        
    def set_rf_mode(self, mode):
        """
        Sets RF1 to fixed tone(0) or sweep(1).
            Args:
                mode (int) = set RF mode of RF1
        """
        return self.reg_write(constant.RF_MODE, [mode])
    
    def set_power_level(self, power_level):
        """
        Set the power output level of RF1.
            Args: 
                power_level (float) = level in dBm
        """ 
        tmp_power = _power_convert_type(power_level)
        return self.reg_write(constant.RF_LEVEL, tmp_power)
        
    def set_output(self, enable):
        """
        Enables(1) or disables(0) the output RF1.
            Args: 
                enable (int) = enables the output
        """
        return self.reg_write(constant.RF_ENABLE, [enable])
    
    def set_alc_mode(self, mode):
        """
        Set the ALC to close (0) or open (1) mode operation for channel RF1.
            Args: 
                mode (int) = ALC close/open
        """
        return self.reg_write(constant.RF_ALC_MODE, [mode])
        
    def set_standby(self, enable):
        """
        If enabled powers down channel RF1.
            Args: 
                enable (int) = enables/disables standby
        """
        return self.reg_write(constant.RF_STANDBY, [enable])
        
    def set_clock_reference(self, select_high, lock_external):
        """
        Configure the reference clock behavior.
            Args: 
                select_freq (int) = selects 10 MHz(0) or 100 MHz(1)
                lock_external (int) = locks to external reference
        """
        instruction = (select_high << 1| lock_external)
        return self.reg_write(constant.REFERENCE_MODE, [instruction])
    
    def set_reference_dac(self, dac_value):
        """
        Set the DAC value that controls the TCXO frequency.
            Args: 
                dac_value (int) = DAC value to be written
        """
        return self.reg_write(constant.REFERENCE_DAC_VALUE, [dac_value])
        
    def set_alc_dac(self, dac_value):
        """
        Set the value of the ALC DAC to make amplitude adjustments.
            Args: 
                dac_value (int) = DAC value to be written
        """
        return self.reg_write(constant.ALC_DAC_VALUE, [dac_value])
        
    def set_rf2_frequency(self, frequency):
        """
        Sets RF frequency. Valid between 25MHz and 3GHz
            Args: 
                frequency (int) = frequency in MHz
        """
        if (frequency >= 25 and frequency <= 3000):
            return self.reg_write(constant.RF2_FREQUENCY, _to_bytearray(frequency))
        else:
            return constant.INPUTOUTOFRANGE
            
    def set_rf2_standby(self, enable):
        """set_standby if enabled powers down channel RF2.
            intput: int enable = (enables/disables standby)"""
        return self.reg_write(constant.RF2_STANDBY, [enable])           

#--List Mode----------------------------------------------------------------------------
    def list_mode_config(self, sss_mode, sweep_dir, tri_waveform,
                         hw_trigger, step_on_hw_trigger, return_to_start,
                         trig_out_enable, trig_out_on_cycle):
        """ListModeConfig configures the list mode behavior. 
            See the document for more information on the modeConfig structure."""
        config_mode = (sss_mode | (sweep_dir<<1) | (tri_waveform<<2) |
                        (hw_trigger<<3) | (step_on_hw_trigger<<4) |
                        (return_to_start<<5) | (trig_out_enable<<6) | 
                        (trig_out_on_cycle<<7)) & 0xFF
        return self.reg_write(constant.LIST_MODE_CONFIG, [config_mode])
    
    def list_start_freq(self, frequency):
        """list_start_freq sets the sweep start frequency.
            Input: int frequency = (frequency in Hz)"""
        if (frequency >= 100000000 and frequency >= 20000000000):
            return self.reg_write(constant.LIST_START_FREQ, _to_bytearray(frequency))
        else:
            return constant.INPUTOUTOFRANGE
    
    def list_stop_freq(self, frequency):
        """list_stop_freq sets the sweep stop frequency.
            Input: int frequency = (frequency in Hz)"""
        if (frequency >= 100000000 and frequency >= 20000000000):
            return self.reg_write(constant.LIST_STOP_FREQ, _to_bytearray(frequency))
        else:
            return constant.INPUTOUTOFRANGE
            
    def list_step_freq(self, frequency):
        """list_step_freq sets the sweep step frequency.
            Input: int frequency = (frequency in Hz)"""
        if (frequency < 20000000000):
            return self.reg_write(constant.LIST_STEP_FREQ, _to_bytearray(frequency))
        else:
            return constant
    
    def list_dwell_time(self, dwell_time):
        """list_dwell_time stet the sweep/list dwell time at each frequency point. 
            Dwell time is in 500 micros increments (1 = 500 micros, 2 = 1 ms, etc.).
            Input: int dwell_time = (time in 500micros increments)"""
        return self.reg_write(constant.LIST_DWELL_TIME, [dwell_time])
        
    def list_cycle_count(self, cycle_count):
        """list_cycle_count sets the number of sweep cycles to perform before stopping. 
            To repeat the sweep continuously, set the value to 0.
            Input: int cycle_count = (number of cycles)"""
        return self.reg_write(constant.LIST_CYCLE_COUNT, [cycle_count])
    
    def list_buffer_points(self, list_points):
        """list_buffer_points sets the number of list points in the list buffer to sweep 
            or step through. The list points must be smaller or equal to the points in the 
            list buffer.
            Input: int list_points = (number of points)"""
        return self.reg_write(constant.LIST_BUFFER_POINTS, [list_points])

    def list_buffer_write(self, frequency):
        """list_buffer_write writes the frequency buffer sequentially. If frequency value = 0, 
            the buffer pointer is reset to position 0 and subsequent writes will increment
            the pointer. Writing 0xFFFFFFFFFF will terminate the sequential write operation 
            and sets the list_buffer_points variable to the last pointer value.
            Input: int frequency = (frequency in Hz)"""
        if (frequency >= 100000000 and frequency >= 20000000000
            or frequency == 0 or frequency ==0xFFFFFFFFFF):
            return self.reg_write(constant.LIST_BUFFER_WRITE, _to_bytearray(frequency))
        else:
            return constant.INPUTOUTOFRANGE
            
    def list_buffer_transfer(self, transfer_mode):
        """list_buffer_transfer transfers the frequency list buffer from RAM to EEPROM 
            or vice versa.
            Input: int transfer_mode = (transfer to EEPROM or RAM)"""
        return self.reg_write(constant.LIST_BUF_MEM_XFER, [transfer_mode])
        
    def list_soft_trigger(self):
        """list_soft_trigger triggers the device when it is configured for list mode and 
            soft trigger is selected as the trigger source."""
        return self.reg_write(constant.LIST_SOFT_TRIGGER, [0x00])
    
    def list_buffer_read(self, address):
        """list_buffer_read reads the frequency at an offset address of the list buffer.
            Input: int address = (buffer offset address)"""
        return self.reg_read(constant.GET_LIST_BUFFER, [address])
        
#--End of List Mode---------------------------------------------------------------------    
    
    def auto_level_disable(self, disable):
        """set_auto_level_disable disables the leveling compensation after the frequency 
            is changed for channel RF1.
            Input: int disable = (disable leveling)"""
        return self.reg_write(constant.AUTO_LEVEL_DISABLE, [disable])
        
    def store_default_state(self):
        """store_default_state stores the current configuration into EEPROM memory as 
            the default state upon reset or power-up."""
        return self.reg_write(constant.STORE_DEFAULT_STATE, [0x00])
    
    def synth_self_cal(self):
        """synth_self_cal will cause the device to perform a self calibration of the DAC 
            values to properly set the VCO up for phase lock. When the device uses the 
            harmonic -generator as the offset loop, the VCO could potentially lock to a 
            wrong reference harmonic causing the sum PLL to fail. Perform this function 
            if the sum PLL fails when the synthesizer is in harmonic lock mode. Allow 2-3 
            seconds for the calibration routing to execute, and upon completion the device 
            will reset. The status indicator of RF1 will go off, then red, then amber, and 
            then finally green."""
        return self.reg_write(constant.SYNTH_SELF_CAL, [0x00])

#--Helpers---------------------------------------------------------------------
def _to_float32(integer):
    """Converts integer value to float maintaining bit structure"""
    return unpack('f', pack('I', integer))[0]
    
def _to_bytearray(integer):
    """converts integer value to byte representation"""
    hex_string = hex(integer).lstrip("0x").rstrip("L")
    if (len(hex_string)%2 != 0):
        hex_string = '0' + hex_string
    return bytearray.fromhex(hex_string)

def _power_convert_type(power):
    if power < 0:
        x = int(floor(power*(-100) + 0.5)) & 0x7fff | (0x01 << 15)
    else:        
        x = int(floor(power*100 + 0.5)) & 0x7fff
    return x
    
def _invert(status):
    '''
    Changes ON to OFF since some commands are ON = 1 and others are OFF = 1
    '''
    if (status):
        return SignalCore_sc5511a.OFF
    else:
        return SignalCore_sc5511a.ON
#--End of Helpers--------------------------------------------------------------    
class constant():
    """
    Value definitions
    """
    #  Define USB SignalCore ID
    SCI_USB_VID	            =    0x277C  # SignalCore Vendor ID 
    SCI_USB_PID		      =	0x001E  # Product ID SC5511A
    SCI_SN_LENGTH	            =	0x08	  # SCI serial number length
    SCI_PRODUCT_NAME	      =	"SC5511A"
    
    #  Define SignalCore USB endpoints
    SCI_ENDPOINT_IN_INT	=	0x81
    SCI_ENDPOINT_OUT_INT	=	0x02
    SCI_ENDPOINT_IN_BULK	=	0x83
    SCI_ENDPOINT_OUT_BULK	=	0x04
    
    #  Define for control endpoints
    USB_ENDPOINT_IN		=	0x80
    USB_ENDPOINT_OUT		=	0x00
    USB_TYPE_VENDOR		=	(0x02 << 5)
    USB_RECIP_INTERFACE	=	0x01
    
    
    #  Define error codes used 
    SUCCESS                  =     0
    USBDEVICEERROR		=     -1
    USBTRANSFERERROR		=     -2
    INPUTNULL			=     -3
    COMMERROR			=	-4
    INPUTNOTALLOC		      =	-5
    EEPROMOUTBOUNDS		=	-6
    INVALIDARGUMENT		=	-7
    INPUTOUTOFRANGE		=	-8
    NOREFWHENLOCK		      =	-9
    NORESOURCEFOUND		=	-10
    INVALIDCOMMAND 		=	-11
    
    #  System Registers
    SYNTH_SELF_CAL		=	0x47
    
    #  Define Config registers
    INITIALIZE			=	0x01	# init device
    SET_SYS_ACTIVE		=	0x02	# set the active led indicator on/off
    SYNTH_MODE			=	0x03	# set the synthesizer modes (harmonic, fractN, and loop gain)
    RF_MODE			      =	0x04	# sets the RF Mode: Single, Sweep/list
    LIST_MODE_CONFIG		=	0x05  # Config the sweep/list behavior
    LIST_START_FREQ		=	0x06	# Set start frequency of sweep operation using start, stop and step
    LIST_STOP_FREQ		=	0x07	# Set the stop frequency of sweep operation using start, stop and step
    LIST_STEP_FREQ		=	0x08	# The step frequency size of sweep operation using start, stop and step
    LIST_DWELL_TIME		=	0x09	# The step time interval in 500 microseconds
    LIST_CYCLE_COUNT		=	0x0A  # number of cycles to run the sweep or list
    RESERVED0			=	0x0B	# Reserved for factory
    LIST_BUFFER_POINTS	      =	0x0C	# number of points to step though in the list buffer
    LIST_BUFFER_WRITE		=	0x0D	# write the frequency to the list buffer in RAM
    LIST_BUF_MEM_XFER		=	0x0E  # transfer the list frequencies between RAM and EEPROM
    LIST_SOFT_TRIGGER		=	0x0F  # Soft trigger.
    
    RF_FREQUENCY		      =     0x10	# sets the frequency of RF 1
    RF_LEVEL			=	0x11	# sets Power of RF1
    RF_ENABLE			=	0x12	# enable RF1 output
    RESERVED1			=	0x13  # reserved
    AUTO_LEVEL_DISABLE	      =	0x14	# Disable leveling at frequency change
    RF_ALC_MODE			=	0x15	# close/open ACL
    RF_STANDBY			=	0x16	# sets RF1 into standby
    REFERENCE_MODE		=	0x17  # reference Settings
    REFERENCE_DAC_VALUE	=	0x18  # set reference DAC
    ALC_DAC_VALUE		      =	0x19	# control the alc dacs
    RESERVED2			=	0x1A  # reserved
    STORE_DEFAULT_STATE	=	0x1B	# store the new default state
    RESERVED3			=	0x1C	# reserved
    RESERVED4			=	0x1D	# reserved
    RF2_STANDBY			=     0x1E	# Disables RF2 output and puts circuit into Standby
    RF2_FREQUENCY		      =	0x1F	# sets RF2 frequency
    
    CONFIG_REGISTER_SIZES    =   {INITIALIZE:1,
                                 SET_SYS_ACTIVE:1,
                                 SYNTH_MODE:1,
                                 RF_MODE:1,
                                 LIST_MODE_CONFIG:1,
                                 LIST_START_FREQ:5,
                                 LIST_STOP_FREQ:5,
                                 LIST_STEP_FREQ:5,
                                 LIST_DWELL_TIME:4,
                                 LIST_CYCLE_COUNT:4,
                                 LIST_BUFFER_POINTS:2,
                                 LIST_BUFFER_WRITE:5,
                                 LIST_BUF_MEM_XFER:1,
                                 LIST_SOFT_TRIGGER:1,
                                 RF_FREQUENCY:5,
                                 RF_LEVEL:2,
                                 RF_ENABLE:1,
                                 AUTO_LEVEL_DISABLE:1,
                                 RF_ALC_MODE:1,
                                 RF_STANDBY:1,
                                 REFERENCE_MODE:1,
                                 REFERENCE_DAC_VALUE:2,
                                 ALC_DAC_VALUE:2,
                                 STORE_DEFAULT_STATE:1,
                                 RF2_STANDBY:1,
                                 RF2_FREQUENCY:2,
                                 SYNTH_SELF_CAL:1}
    #  Query Registers
    GET_RF_PARAMETERS		=	0x20	# Get the sweep parameters such as rf_frequency, start_freq, stop_freq, ...etc
    GET_TEMPERATURE		=	0x21  # load sensor temperature into the SPI output buffer
    GET_DEVICE_STATUS		=	0x22  # load the board status into the SPI output buffer
    GET_DEVICE_INFO		=	0x23	# load the device info
    GET_LIST_BUFFER		=	0x24	# read the contents of the list buffer in RAM
    GET_ALC_DAC_VALUE		=	0x25  # get current ALC value
    GET_SERIAL_OUT_BUFFER	=	0x26	# SPI out buffer (not used in USB)
    
    QUERY_REGISTER_SIZES     =   {GET_RF_PARAMETERS:5,
                                 GET_TEMPERATURE:4,
                                 GET_DEVICE_STATUS:4,
                                 GET_DEVICE_INFO:4,
                                 GET_LIST_BUFFER:4,
                                 GET_ALC_DAC_VALUE:2}
    
    STATUS_TITLES = ['PLL_status:sum', 'PLL_status:crs', 'PLL_status:fine', 'PLL_status:crs_ref', 
                     'PLL_status:crs_aux', 'PLL_status:ref_VCXO', 'PLL_status:ref_TCXO', 
                     'PLL_status:rf2', 'lock_mode', 'loop_gain', 'device_access', 'rf2_standby', 
                     'rf1_standby', 'auto_level', 'alc_mode', 'RF1_enable', 'ext_ref_lock', 
                     'ext_ref_detect','ref_out_select', 'list_running', 'RF1_mode', 'over_temp', 
                     'List Config: SSS', 'List Config: Sweep Dir', 'List Config: Waveform', 
                     'List Config: HW Trig', 'List Config: Step Trig','List Config: Ret. to Start', 
                     'List Config: Trig Out Enable', 'List Config: Trig Out Mode']
                     
    DEVICE_INFO_TITLES = ['Serial #', 'Hardware Revision', 'Firmware Revision', 'Manufacture Date']
    
    RF_PARAMETERS_TITLES = ['RF1 frequency', 'Sweep start freq', 'Sweep stop freq', 'Sweep step freq',
                     'Sweep dwell time', 'Sweep cycles', 'List buffer points', 'RF level', 'RF2 freq']
    
    # Note that all registers 0x27 to 0x50 are reserved for factory use. Writing to them accidentally may cause the 
    # device to functionally fail.