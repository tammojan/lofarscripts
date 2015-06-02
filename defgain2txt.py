#!/usr/bin/env python

from pyrap.tables import table
import argparse
import numpy as np
import cmath
import scipy.io
import sys

def gain2matlab(parmdb):
  deftable=table(parmdb+"::DEFAULTVALUES",ack=False)

  vals=deftable.col('VALUES')
  names=deftable.col('NAME')

  gains={}
  for i in range(names.nrows()):
    if names[i].split(':')[0]=='Gain':
      antname=names[i].split(':')[-1]
      val=vals[i][0][0]
      if names[i].split(':')[-2]=='Real':
        if antname in gains:
          gains[antname]+=val+0j
        else:
          gains[antname]=val+0j
      elif names[i].split(':')[-2]=='Imag':
        if antname in gains:
          gains[antname]+=val*1j
        else:
          gains[antname]=val*1j
         

  for ant in gains:
    print ant,
    print abs(gains[ant]),
    print gains[ant]


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = "Extract default gains from an instrument file")
  parser.add_argument("instrumentfile", help="Name of instrument table")

  args = parser.parse_args()

  gain2matlab(args.instrumentfile)
