# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 10:54:45 2016

@author: HatLabUnderGrads
"""

import matplotlib.pyplot as plt
import numpy as np
import time
import sys
fig = plt.figure()
ax = fig.add_subplot(111)
plt.rcParams['keymap.yscale'] = ''
text = plt.text(.5,.5, 'Test Text')

# Makes the plot interactive
plt.ion()
pause = False
def on_key(event):
    text.set_text('You pressed %s' %event.key)
    if event.key == u'l':
        global pause
        pause = not pause
    sys.stdout.flush()
    
def onclick(event):
    print event.button
# waits for .5 seconds and changes the text to NEW
plt.pause(.5)
text.set_text('NEW')
#cid = plt.gcf().canvas.mpl_connect('key_press_event', on_key)
cdi = fig.canvas.mpl_connect('key_press_event', on_key)
cdb = fig.canvas.mpl_connect('button_press_event',onclick)
# An example way to wait for one second and then update the text displayed on the screen

i = 0
x = np.array([i])
y = np.random.rand(1)
line, = ax.plot(x)

while i < 10:
    while pause:
        print plt.waitforbuttonpress()
    plt.pause(1)
    #plt.pause(.1)
    text.set_text('Iteration %s' %i)
    print x
    print y
    if len(y)>1:
        ax.set_ylim([0,1])
        ax.set_xlim([0,x.shape[0]-1])
        line.set_xdata(x)
        line.set_ydata(y)    
    x = np.append(x,i+1)
    y = np.append(y, np.random.rand(1))
    i+=1
    plt.draw()
plt.show(block=True)
plt.close() 