#!/usr/bin/env python
#
# Script to add dummy tabrefcodes to a MS.
# Do not use this script unless you want a measurement set to work with 
# casacore version 2.0.3, and it didn't work without it.
# Newer and older versions of casacore accept MSs without tabrefcodes.

import casacore.tables as pt
import sys
from numpy import uint32, record, array

t = pt.table(sys.argv[1]+'::SPECTRAL_WINDOW', readonly=False)

for colnm in ['CHAN_FREQ','REF_FREQUENCY']:
  tc = t.col(colnm)
  record=tc.getkeyword('MEASINFO')
  record['TabRefCodes']=array([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=uint32)
  record['TabRefTypes']=['REST', 'LSRK', 'LSRD', 'BARY', 'GEO', 'TOPO', 'GALACTO', 'LGROUP', 'CMB']
  tc.putkeyword('MEASINFO',record)
