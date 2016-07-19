# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 10:54:45 2016

@author: HatLabUnderGrads
"""

import matplotlib.pyplot as plt

text = plt.text(.5,.5, 'Test Text')

# Makes the plot interactive
plt.ion()
# waits for .5 seconds and changes the text to NEW
plt.pause(.5)
text.set_text('NEW')

# An example way to wait for one second and then update the text displayed on the screen
i = 0
while i < 10:
    plt.pause(1)
    text.set_text('Iteration %s' %i)
    i+=1