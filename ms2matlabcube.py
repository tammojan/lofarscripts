#!/usr/bin/env python

from pyrap.tables import table, taql
from math import sqrt
import numpy as np
import scipy.io
import argparse
import sys

def ms2matlabcube(datacolname='DATA',msname='test1.MS',visfilename='bbsvis.mat',modelcolname='MODEL_DATA',applyweights=True):
  """converts a measurement set to a matlab file"""
  t0=table(msname,ack=False)

  t=taql('SELECT DISTINCT TIME from $t0');
  ntimes=t.nrows();
  print "Num times:",ntimes

  t=taql('SELECT DATA from $t0 LIMIT 1');
  tmp=t.col('DATA');
  nch=tmp[0].shape[0];
  print "Num channels:",nch

  t=taql('select DISTINCT ANTENNA1 from $t0');
  nants=t.nrows();
  print "Num ants:",nants
 
  V  = np.zeros((nants*2,nants*2,ntimes,nch),dtype=np.complex)
  Vm = np.zeros((nants*2,nants*2,ntimes,nch),dtype=np.complex)
  W  = np.zeros((nants*2,nants*2,ntimes,nch),dtype=np.float)

  for ch in range(nch):
    print "Channel",ch
    for timeslot in range(ntimes):
      print "Timeslot",timeslot
      t=taql('SELECT *, MAX(WEIGHT_SPECTRUM) as MW FROM $t0 WHERE TIME IN (SELECT DISTINCT TIME FROM $t0 OFFSET $timeslot LIMIT 1)')

      data=t.col(datacolname)
      flag=t.col('FLAG')
      model=t.col(modelcolname)
      weight=t.col('WEIGHT_SPECTRUM')
      print weight.getdesc()

      print data[0][ch][0]

      antenna1=t.col('ANTENNA1')
      antenna2=t.col('ANTENNA2')

      for bl in range(data.nrows()):
        ant1=antenna1[bl]
        ant2=antenna2[bl]
        if ant1==ant2:
          continue
        for cor in range(4):
          if not flag[bl][0][cor]:
            if applyweights:
              V[ 2*ant1+cor/2][2*ant2+cor%2][ timeslot][ch] = data[bl][ch][cor]*sqrt(weight[bl][ch][cor])
              Vm[2*ant1+cor/2][2*ant2+cor%2][ timeslot][ch] =model[bl][ch][cor]*sqrt(weight[bl][ch][cor])
              # symmmetry
              V[ 2*ant2+cor%2][2*ant1+cor/2][ timeslot][ch] =( data[bl][ch][cor]*sqrt(weight[bl][ch][cor])).conjugate()
              Vm[2*ant2+cor%2][2*ant1+cor/2][ timeslot][ch] =(model[bl][ch][cor]*sqrt(weight[bl][ch][cor])).conjugate()
            else:
              V[ 2*ant1+cor/2][2*ant2+cor%2][ timeslot][ch] =  data[bl][ch][cor]
              Vm[2*ant1+cor/2][2*ant2+cor%2][ timeslot][ch] = model[bl][ch][cor]
              #W[ 2*ant1+cor/2][2*ant2+cor%2][ timeslot][ch] =weight[bl][ch][cor]
              # symmetry
              V[ 2*ant2+cor%2][2*ant1+cor/2][ timeslot][ch] =(  data[bl][ch][cor]).conjugate()
              Vm[2*ant2+cor%2][2*ant1+cor/2][ timeslot][ch] =( model[bl][ch][cor]).conjugate()
              #W[ timeslot][ch][2*ant2+cor%2][2*ant1+cor/2] =weight[bl][ch][cor]
    
      
  if applyweights:
    scipy.io.savemat(visfilename, dict(Vcube=V, Vmcube=Vm), oned_as="row")
  else:
    scipy.io.savemat(visfilename, dict(Vcube=V, Vmcube=Vm, Wgtcube=W), oned_as="row")

  print "Stored timeslot", timeslot, "of column", datacolname, "of file", msname, "as", visfilename
  print "Stored timeslot", timeslot, "of column", modelcolname, "of file", msname, "in", visfilename
  #if not applyweights:
    #print "Stored timeslot", timeslot, "weights of file", msname, "in", visfilename

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = "Extract data and model data from a MS, save in matlab format")
  parser.add_argument("msname", help="Name of the MS that contains data, model data and instrument table")
  parser.add_argument("-d", "--datacolname", help="Data column name", default="DATA")
  parser.add_argument("-m", "--modelcolname", help="Model column name", default="MODEL_DATA")
  parser.add_argument("-o", "--output", help="Save output in this output file", default="bbsvis.mat")
  parser.add_argument("-nw", "--no-weights", help="Do not apply weights, store them separately in the outputfile", action='store_true')

  args = parser.parse_args()

  ms2matlabcube(msname=args.msname,datacolname=args.datacolname,modelcolname=args.modelcolname,applyweights=(not args.no_weights),visfilename=args.output)
