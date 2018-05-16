#!/usr/bin/env python

from casacore.tables import table, taql
from math import sqrt
import numpy as np
import scipy.io
import argparse
import sys

def ms2matlab(datacolname='DATA',msname='test1.MS',visfilename='bbsvis.mat',timeslot=0,modelcolname='MODEL_DATA',applyweights=True,channel=0):
  """converts a measurement set to a matlab file"""
  t0=table(msname,ack=False)

  t=taql('SELECT *, MAX(WEIGHT_SPECTRUM) as MW FROM $t0 WHERE TIME IN (SELECT DISTINCT TIME FROM $t0 OFFSET $timeslot LIMIT 1)')

  data=t.col(datacolname)
  flag=t.col('FLAG')
  model=t.col(modelcolname)
  weight=t.col('WEIGHT_SPECTRUM')

  antenna1=t.col('ANTENNA1')
  antenna2=t.col('ANTENNA2')

  nants=len(set(antenna1))

  V  = np.zeros((nants*2,nants*2),dtype=np.complex)
  Vm = np.zeros((nants*2,nants*2),dtype=np.complex)
  W  = np.zeros((nants*2,nants*2),dtype=np.float)

  for i in range(data.nrows()):
    ant1=antenna1[i]
    ant2=antenna2[i]
    if ant1==ant2:
      continue
    for cor in range(4):
      if not flag[i][0][cor]:
        if applyweights:
          V[ 2*ant1+cor/2][2*ant2+cor%2] = data[i][channel][cor]*sqrt(weight[i][0][cor])
          Vm[2*ant1+cor/2][2*ant2+cor%2] =model[i][channel][cor]*sqrt(weight[i][0][cor])
        else:
          V[ 2*ant1+cor/2][2*ant2+cor%2] =  data[i][channel][cor]
          Vm[2*ant1+cor/2][2*ant2+cor%2] = model[i][channel][cor]
          W[ 2*ant1+cor/2][2*ant2+cor%2] =weight[i][channel][cor]
  
  if applyweights:
    scipy.io.savemat(visfilename, dict(V=V, Vm=Vm), oned_as="row")
  else:
    scipy.io.savemat(visfilename, dict(V=V, Vm=Vm, Wgt=W), oned_as="row")

  print("Stored timeslot", timeslot, " channel", channel, "of column", datacolname, "of file", msname, "as", visfilename)
  print("Stored timeslot", timeslot, " channel", channel, "of column", modelcolname, "of file", msname, "in", visfilename)
  if not applyweights:
    print("Stored timeslot", timeslot, "weights of file", msname, "in", visfilename)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = "Extract data and model data from a MS, save in matlab format")
  parser.add_argument("msname", help="Name of the MS that contains data, model data and instrument table")
  parser.add_argument("-d", "--datacolname", help="Data column name", default="DATA")
  parser.add_argument("-m", "--modelcolname", help="Model column name", default="MODEL_DATA")
  parser.add_argument("-t", "--timeslot", help="Time slot from MS", type=int, default=0)
  parser.add_argument("-c", "--channel", help="Channel from MS", type=int, default=0)
  parser.add_argument("-o", "--output", help="Save output in this output file", default="bbsvis.mat")
  parser.add_argument("-nw", "--no-weights", help="Do not apply weights, store them separately in the outputfile", action='store_true')

  args = parser.parse_args()

  ms2matlab(msname=args.msname,datacolname=args.datacolname,timeslot=args.timeslot,modelcolname=args.modelcolname,applyweights=(not args.no_weights),visfilename=args.output,channel=args.channel)
