#!/usr/bin/env python
from __future__ import print_function

import sys
import casacore.tables as pt
import argparse

def main(msname):
    t=pt.table(msname+'/LOFAR_ANTENNA_FIELD', readonly=False, ack=False)
    kw=t.getcolkeywords("COORDINATE_AXES")
    # {'QuantumUnits': ['m', 'm'], 'MEASINFO': {'Ref': 'ITRF', 'type': 'direction'}}
    measinfotype=kw['MEASINFO']['type']
    if kw['MEASINFO']['type']=='position' and kw['QuantumUnits']==['m','m','m']:
        print('Measurement set',msname,'was already fixed.')
        return
    kw['MEASINFO']['type']='position'
    kw['QuantumUnits']=['m','m','m']
    t.putcolkeywords("COORDINATE_AXES", kw)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description = "Fix the units in the LOFAR_ANTENNA_FIELD table")
    parser.add_argument("msname", help="Name of the measurement set")
    print("Fixed column units in", msname)
    main(sys.argv[1])
