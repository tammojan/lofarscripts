#!/usr/bin/env python

from casacore import tables as pt
from shutil import move
import numpy

# Create main table
t = pt.table('instrument', {\
               'NAMEID':     {'valueType': 'uint'},\
               'STARTX':     {'valueType': 'double'},\
               'STARTY':     {'valueType': 'double'},\
               'ENDY':       {'valueType': 'double'},\
               'ENDX':       {'valueType': 'double'},\
               'ERRORS':     {'valueType': 'double', 'ndim': -1, '_c_order': True},\
               'VALUES':     {'valueType': 'double', 'ndim': -1, '_c_order': True},\
               'INTERVALSX': {'valueType': 'double', 'ndim': -1, '_c_order': True},\
               'INTERVALSY': {'valueType': 'double', 'ndim': -1, '_c_order': True} \
            })
t.close()

# Create names table and move it inside main table
names = pt.table('NAMES', {\
               'NAME':         {'valueType': 'string'},\
               'FUNKLETTYPE':  {'valueType': 'int'},\
               'NX':           {'valueType': 'int'},\
               'NY':           {'valueType': 'int'},\
               'PERTURBATION': {'valueType': 'double'},\
               'PERT_REL':     {'valueType': 'boolean'},\
               'SOLVABLE':     {'valueType': 'boolean', 'ndim': -1, '_c_order': True}\
            })
names.close()
move('NAMES', 'instrument/NAMES')

# Create default values table and move it inside main table
defvalues = pt.table('DEFAULTVALUES', {\
               'DOMAIN': {'_c_order': True, 'ndim': -1, 'valueType': 'double'},\
               'FUNKLETTYPE': { 'valueType': 'int'},\
               'NAME': { 'valueType': 'string'},\
               'PERTURBATION': { 'valueType': 'double'},\
               'PERT_REL': { 'valueType': 'boolean'},\
               'SOLVABLE': {'_c_order': True, 'ndim': -1, 'valueType': 'boolean'},\
               'VALUES': {'_c_order': True, 'ndim': -1, 'valueType': 'double'}\
            })
defvalues.close()
move('DEFAULTVALUES', 'instrument/DEFAULTVALUES')

# Make tables subtables
t = pt.table('instrument', readonly=False)
names=pt.table('instrument/NAMES', readonly=False)
t.putkeyword('NAMES', names, makesubrecord=True)
defvalues=pt.table('instrument/DEFAULTVALUES', readonly=False)
t.putkeyword('DEFAULTVALUES', defvalues, makesubrecord=True)

# Now we have an empty table, below some examples of how to add values to it

varnames=["Gain:0:0:Real:CS001HBA0", "Gain:0:0:Imag:CS001HBA0", "Gain:1:1:Real:CS001HBA0", "Gain:1:1:Imag:CS001HBA0", "Gain:0:0:Real:CS002HBA0", "Gain:0:0:Imag:CS002HBA0", "Gain:1:1:Real:CS002HBA0", "Gain:1:1:Imag:CS002HBA0", "Gain:0:0:Real:CS002HBA1", "Gain:0:0:Imag:CS002HBA1", "Gain:1:1:Real:CS002HBA1", "Gain:1:1:Imag:CS002HBA1", "Gain:0:0:Real:CS004HBA1", "Gain:0:0:Imag:CS004HBA1", "Gain:1:1:Real:CS004HBA1", "Gain:1:1:Imag:CS004HBA1", "Gain:0:0:Real:RS106HBA", "Gain:0:0:Imag:RS106HBA", "Gain:1:1:Real:RS106HBA", "Gain:1:1:Imag:RS106HBA", "Gain:0:0:Real:RS208HBA", "Gain:0:0:Imag:RS208HBA", "Gain:1:1:Real:RS208HBA", "Gain:1:1:Imag:RS208HBA", "Gain:0:0:Real:RS305HBA", "Gain:0:0:Imag:RS305HBA", "Gain:1:1:Real:RS305HBA", "Gain:1:1:Imag:RS305HBA", "Gain:0:0:Real:RS307HBA", "Gain:0:0:Imag:RS307HBA", "Gain:1:1:Real:RS307HBA", "Gain:1:1:Imag:RS307HBA"]

defvalues.addrows()
defvalues.putcell("NAME", defvalues.nrows()-1, "Gain:0:0:Real")
defvalues.putcell("VALUES", defvalues.nrows()-1, numpy.array([[1.]]))
defvalues.addrows()
defvalues.putcell("NAME", defvalues.nrows()-1, "Gain:1:1:Real")
defvalues.putcell("VALUES", defvalues.nrows()-1, numpy.array([[1.]]))

starttime=float(pt.taql("CALC str(2013/03/29/13:59:48,'%21.21f')")[0])

for num, name in enumerate(varnames):
  # Add name and nameid
  names.addrows()
  nameid=names.nrows()-1
  names.putcell("NAME", nameid, name)

  # Add values
  t.addrows()
  trownum=t.nrows()-1
  t.putcell("VALUES", trownum, numpy.array([[1.]])) # Should be correct shape
  t.putcell("STARTX", trownum, 1.34276e+08) # Start frequency in Hz
  t.putcell("ENDX",   trownum, 1.34471e+08) # End frequency in Hz
  t.putcell("STARTY", trownum, starttime) # Start time in s
  t.putcell("ENDY",   trownum, starttime+80) # End time in s
  t.putcell("NAMEID", trownum, nameid)
