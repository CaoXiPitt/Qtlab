example1 = qt.instruments.create('example1', 'example', address='GPIB::1', reset=True)
dsgen = qt.instruments.create('dsgen', 'dummy_signal_generator')
pos = qt.instruments.create('pos', 'dummy_positioner')
combined = qt.instruments.create('combined', 'virtual_composite')
VNA= qt.instruments.create('VNA','Agilent_ENA_5071C', address='TCPIP0::169.254.169.64::inst0::INSTR')
#AWG = qt.instruments.create('AWG','AWG5014C', address='TCPIP0::169.254.47.254::inst0::INSTR')
#MXA = qt.instruments.create('MXA','Aglient_MXA_N9020A',address='TCPIP0::169.254.180.116::INSTR')
MXA = qt.instruments.create('MXA','Keysight_MXA_N9020A',address='TCPIP0::169.254.180.116::INSTR')
SWT = qt.instruments.create('SWT','Mini_CircuitsSwitch',address='http://169.254.47.255')
YOKO = qt.instruments.create('YOKO', 'Yokogawa_GS200', address='TCPIP0::169.254.47.130::INSTR')
#GEN = qt.instruments.create('GEN','SignalCore_sc5511a')
EXG = qt.instruments.create('GEN', 'Keysight_N5183B', address='TCPIP0::169.254.21.181::inst0::INSTR', reset = False)
RecordTest = qt.instruments.create('RecordTest','RecordTest_driver',address='GPIB::2')
combined.add_variable_scaled('magnet', example1, 'chA_output', 0.02, -0.13, units='mT')

#combined.add_variable_combined('waveoffset', [{
#    'instrument': dmm1,
#    'parameter': 'ch2_output',
#    'scale': 1,
#    'offset': 0}, {
#    'instrument': dsgen,
#    'parameter': 'wave',
#    'scale': 0.5,
#    'offset': 0
#    }], format='%.04f')
