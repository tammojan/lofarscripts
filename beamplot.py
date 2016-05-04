#!/usr/bin/env python

from __future__ import print_function

from lofar.stationresponse import stationresponse
import casacore.tables as pt
import numpy as np

msname="~/leah.MS"

sr = stationresponse(msname=msname, inverse=False, useElementResponse=True, useArrayFactor=True, useChanFreq=True)

ms = pt.table(msname, ack=False)

time = ms.getcol('TIME')[0]

#sr.setDirection(myra_in_rad, mydec_in_rad) # default is phase center

itrfdir = sr.getDirection(time)
refdelay = sr.getRefDelay(time)
reftile = sr.getRefTile(time)

freqtable = pt.table(msname+'::SPECTRAL_WINDOW')
freqs = freqtable[0]['CHAN_FREQ']

station = 0

for freq in freqs:
    bj = sr.evaluateFreqITRF(time, station, freq, itrfdir, refdelay, reftile)
    # bj is now a 2x2 jones matrix with the modeled beam response
