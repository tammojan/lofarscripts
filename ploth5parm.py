#!/usr/bin/env python
from __future__ import print_function

from losoto.h5parm import h5parm
import numpy as np

from matplotlib import pyplot as plt

H = h5parm("testbbs.h5")

tec = H.getSoltabs('sol000')['tec000']
phase = H.getSoltabs('sol000')['scalarphase000']
#antnr = 34
antnr = 20

antname = tec.ant[antnr]

vals = tec.val[0, antnr, 0, :]
vals0 = tec.val[0, 0, 0, :]

plt.plot(vals-vals0, '.')
#plt.ylim([-0.5,0.5])
plt.ylim([-0.125,0.125])
#plt.ylim([-3.15,3.15])
plt.xlim([0,len(vals)])
plt.ylabel("TEC")
plt.xlabel("Time slot")
plt.title("Antenna " + antname)

# Make figure transparent, plot white
ax = plt.gca()
ax.patch.set_facecolor('white')
fig= plt.gcf()
fig.patch.set_alpha(0.0)

# Fit aspect ratio
fig.set_size_inches((8.7,5.5))

plt.savefig('myplot.pdf')
