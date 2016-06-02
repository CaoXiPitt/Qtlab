
#import usb1
import types
#import SC5511A_CONSTANTS as constant
from struct import pack, unpack
from math import floor
from instrument import Instrument

    
class SignalCore_sc5511a(Instrument):
   
    def __init__(self, name, serial_number=None, address=None):
        Instrument.__init__(self, name, tags=['generate'])
        self._serial_number = serial_number
        self.add_parameter('RF1_frequency', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval = 100000000, maxval=20000000000)
        self.add_function('set_freq')
        self.add_function('get_freq')
######## TEST CODE ############################################################
        
    def set_freq(self, freq):
        self._RF1_frequency = freq
    def get_freq(self):
        return self._RF1_frequency
    '''
    def __del__(self):
        if self._handle is not None:
            self._handle.releaseInterface(0)
            self._handle.close()
        else:
            print('Deleting {}'.format(self.serial_number))
    
    def open_device_verbose(self):
        context = usb1.USBContext()
        if self.serial_number is None:
            self._handle = context.openByVendorIDAndProductID(sc5511a.SCI_USB_VID,
                                                    sc5511a.SCI_USB_PID)
        else:
            print("I am a unique device") #debug
        if self._handle is not None:
            self._handle.resetDevice()
            self._handle.setConfiguration(1)
            self._handle.claimInterface(0)
            print("Turn on the LED")    #debug
            command = bytearray([sc5511a.SET_SYS_ACTIVE, 0x01])
            self._handle.controlWrite(0x41, 0, 0, 0, command, 1)
        else:
            print("Device not found") #debug
    
    
           
    def close_device_verbose(self):
        if self.handle is not None:            
            print("Closing device")   #  DEVELOP
            command =  bytearray([sc5511a.SET_SYS_ACTIVE, 0x00])
            self._handle.controlWrite(0x41, 0, 0, 0, command, 1)
            self._handle.releaseInterface(0)
            self._handle.close()
    def get_device_status_verbose(self):
        print("Request for status data")
        command = bytearray([sc5511a.GET_DEVICE_STATUS, 0x00])
        self._handle.controlWrite(0x41, 0, 0, 0, command, 1)
        data = self._handle.controlRead(0x41, 0, 0, 0, 4, 10)  # 4 == size in bytes
        # TODO Decode data in status structure
        return data
        
    def set_frequency_verbose(self, frequency):
        print("Changing the frequency to {}GHz".format(frequency/1,000,000,000))
        command = bytearray([0x10, 0x02, 0x54, 0x0B, 0xE4, 0x00])
        self._handle.controlWrite(0x41, 0, 0, 0, command, 1)
    
          
    def test_float_conversion(self, integer):
        return _to_float32(integer)
####### END TEST CODE #########################################################
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
            print("I am a unique device") #debug
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
            print("Turn on the LED")    #debug
            self.reg_write(constant.SET_SYS_ACTIVE, [0x01])
        else:
            print("Device not found") #debug
            
    def close_device(self):
        if self.handle is not None:            
            print("Closing device")   #debug
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
#--Getters----------------------------------------------------------------------------            

    def get_temperature(self):
        """
        Returns temperature of device
        """
        temp = self.reg_read(constant.GET_TEMPERATURE,[0x00])
        return _to_float32(temp)
        
    def get_rf_parameters(self):
        """
        Gets the current RF parameters such as RF1 frequency, 
        RF2 frequency, and sweep start frequency, etc.
        """
        params = []
        # rf1 freq
        params.append(self.reg_read(constant.GET_RF_PARAMETERS, [0x00]))
        # sweep start freq        
        params.append(self.reg_read(constant.GET_RF_PARAMETERS, [0x01]))
        #sweep stop freq        
        params.append(self.reg_read(constant.GET_RF_PARAMETERS, [0x02]))
        # sweep step freq        
        params.append(self.reg_read(constant.GET_RF_PARAMETERS, [0x03]))
        # sweep dwell time        
        params.append(self.reg_read(constant.GET_RF_PARAMETERS, [0x04])>>8)
        #sweep cycles        
        params.append(self.reg_read(constant.GET_RF_PARAMETERS, [0x05])>>8)
        # list buffer points        
        params.append(self.reg_read(constant.GET_RF_PARAMETERS, [0x06])>>8)
        # rf level
        level = self.reg_read(constant.GET_RF_PARAMETERS, [0x07])>>8        
        params.append(_to_float32(level))
        # rf2 freq        
        params.append(self.reg_read(constant.GET_RF_PARAMETERS, [0x08])>>24)#in MHz
        return params
        
    def get_device_status(self):
        """
        Gets the current device status such as the PLL 
        lock status, sweep modes, and other operating conditions.
        """
        return self.reg_read(constant.GET_DEVICE_STATUS, [0x00])
        
    def get_device_info(self):
        """
        Obtains the device information such as serial number,
        hardware revision, firmware revision, and manufactured date.
        """
        info = []
        # product serial number
        info.append(self.reg_read(constant.GET_DEVICE_INFO, [0x00]))
        # Hardware Revision Conversion
        hrc = self.reg_read(constant.GET_DEVICE_INFO, [0x01])
        info.append(_to_float32(hrc))
        # Firmware Revision Conversion
        frc = self.reg_read(constant.GET_DEVICE_INFO, [0x02])
        info.append(_to_float32(frc))
        # Manufacture Date
        date = self.reg_read(constant.GET_DEVICE_INFO, [0x03])
        info.append([(date>>24) & 0xFF,  # year
                     (date>>16) & 0xFF,  # month
                     (date>>8) & 0xFF,   # day
                     date & 0xFF])       # hour
        return info
        
    def get_alc_dac(self):
        """
        Retrieves the current value of the ALC DAC which set the 
        power level of channel RF1.
        """
        return self.reg_read(constant.GET_ALC_DAC_VALUE, [0x00])
        
#--End of Getters---------------------------------------------------------------------        
#--Setters----------------------------------------------------------------------------            
    def set_frequency(self, frequency):
        """
        Sets RF1 frequency. Valid between 100MHz and 20GHz
            Args:
                frequency (int) = frequency in Hz
        """
        if (frequency >= 100000000 and frequency <= 20000000000):
            return self.reg_write(constant.RF_FREQUENCY, _to_bytearray(frequency))
        else:
            return constant.INPUTOUTOFRANGE
            
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
#--End of Setters-----------------------------------------------------------------------            

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
        if (frequency >= 100000000 and frequency >= 20000000000):
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
        
    """ Value definitions """
    #  Define USB SignalCore ID
    SCI_USB_VID	      =    0x277C  # SignalCore Vendor ID 
    SCI_USB_PID		=	0x001E  # Product ID SC5511A
    SCI_SN_LENGTH	      =	0x08	  # SCI serial number length
    SCI_PRODUCT_NAME	=	"SC5511A"
    
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
    SUCCESS			      =     0
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
    
    RF_FREQUENCY		      =    0x10	# sets the frequency of RF 1
    RF_LEVEL			=	0x11	# sets Power of RF1
    RF_ENABLE			=	0x12	# enable RF1 output
    RESERVED1			=	0x13  # reserved
    AUTO_LEVEL_DISABLE	     =	0x14	# Disable leveling at frequency change
    RF_ALC_MODE			=	0x15	# close/open ACL
    RF_STANDBY			=	0x16	# sets RF1 into standby
    REFERENCE_MODE		=	0x17  # reference Settings
    REFERENCE_DAC_VALUE	=	0x18  # set reference DAC
    ALC_DAC_VALUE		     =	0x19	# control the alc dacs
    RESERVED2			=	0x1A  # reserved
    STORE_DEFAULT_STATE	=	0x1B	# store the new default state
    RESERVED3			=	0x1C	# reserved
    RESERVED4			=	0x1D	# reserved
    RF2_STANDBY			=     0x1E	# Disables RF2 output and puts circuit into Standby
    RF2_FREQUENCY		     =	0x1F	# sets RF2 frequency
    
    #  Query Registers
    GET_RF_PARAMETERS		=	0x20	# Get the sweep parameters such as rf_frequency, start_freq, stop_freq, ...etc
    GET_TEMPERATURE		=	0x21  # load sensor temperature into the SPI output buffer
    GET_DEVICE_STATUS		=	0x22  # load the board status into the SPI output buffer
    GET_DEVICE_INFO		=	0x23	# load the device info
    GET_LIST_BUFFER		=	0x24	# read the contents of the list buffer in RAM
    GET_ALC_DAC_VALUE		=	0x25  # get current ALC value
    GET_SERIAL_OUT_BUFFER	=	0x26	# SPI out buffer (not used in USB)
    QUERY_REGISTER_SIZES    =    {GET_RF_PARAMETERS:5,
                               GET_TEMPERATURE:4,
                               GET_DEVICE_STATUS:4,
                               GET_DEVICE_INFO:4,
                               GET_LIST_BUFFER:4,
                               GET_ALC_DAC_VALUE:2}
    #  System Registers
    SYNTH_SELF_CAL		=	0x47
    
    # Note that all registers 0x27 to 0x50 are reserved for factory use. Writing to them accidentally may cause the 
    # device to functionally fail.
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
#--End of Helpers--------------------------------------------------------------    
def main():
    
    a = sc5511a()
#    a.open_device()
#    print(a.get_device_status())
#    time.sleep(1)
#    a.set_frequency_verbose(10000000000)
#    a.close_device()
    print type(a)    

if __name__ == '__main__':
    main()
'''