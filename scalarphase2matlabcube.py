#!/usr/bin/env python

from pyrap.tables import table
import argparse
import numpy as np
import cmath
import scipy.io
import sys

def scalarphase2matlab(msname='test1.MS', gainfilename='bbsgain.mat', instrumentname='instrument'):
  parmdb=msname+'/'+instrumentname
  antenna=msname+'/ANTENNA'

  valstable=table(parmdb,ack=False)
  namestable=table(parmdb+"::NAMES",ack=False)
  antennatable=table(antenna,ack=False)

  vals=valstable.col('VALUES')
  names=namestable.col('NAME')
  antennas=antennatable.col('NAME')
  antennamap={};
  for i in range(antennas.nrows()):
    antennamap[antennas[i]]=i

  ntimes=vals[0].shape[0]
  nch=vals[0].shape[1]
  print "NTimes:",ntimes,", nch:",nch

  g = np.zeros((len(antennamap),ntimes,nch),dtype=np.complex)

  for ch in range(nch):
    for timeslot in range(ntimes):
      for i in range(vals.nrows()):
        (bla, ant) = names[i].split(':')
        antnr=antennamap[ant]
        val=cmath.rect(1,vals[i][timeslot][ch])
        g[antnr][timeslot][ch]+=val.conjugate()

  scipy.io.savemat(gainfilename, dict(gcube=g), oned_as='row')
  print "Stored gains from", msname, "/",instrumentname,"as",gainfilename

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = "Extract gains from an instrument file, save in matlab format")
  parser.add_argument("msname", help="Name of the MS that contains data, model data and instrument table")
  parser.add_argument("-i", "--instrumentname", help="Name of instrument table", default="instrument")
  parser.add_argument("-o", "--output", help="Save output in this output file", default="bbsgain.mat")

  args = parser.parse_args()

  scalarphase2matlab(msname=args.msname,gainfilename=args.output,instrumentname=args.instrumentname)

