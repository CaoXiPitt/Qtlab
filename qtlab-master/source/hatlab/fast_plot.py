# -*- coding: utf-8 -*-
"""
Created on Fri Aug 05 17:13:14 2016

@author: HATLAB
"""

# Fast plot

import fluxplot


test = fluxplot.FluxSweepPlot()

test.load_data_from_file(h5py_filepath = 'C:\Users\HATLAB\Box Sync\Data\Cooldown_2016_08_05\JPC_00012\Flux_Sweep\signal_sweep_8_5_2016_16_51')

test.plot_data()