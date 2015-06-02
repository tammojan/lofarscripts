#!/usr/bin/env python

from pyrap.tables import table
import argparse
import numpy as np
import cmath
import scipy.io
import sys

def gain2matlab(msname='test1.MS', gainfilename='bbsgain.mat', timeslot=0, instrumentname='instrument'):
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

  g = np.zeros((len(antennamap)*2,2),dtype=np.complex)

  for i in range(vals.nrows()):
    (bla, xcor, ycor, reim, ant) = names[i].split(':')
    antnr=antennamap[ant]
    (xcor,ycor)=(int(xcor),int(ycor))
    if reim=="Real":
      val=vals[i][timeslot][0]
    elif reim=="Imag":
      val=vals[i][timeslot][0]*(1.j)
    elif reim=="Phase":
      val=cmath.rect(1,vals[i][timeslot][0])
    #print antnr, xcor, ycor, antnr*2+xcor, ycor, val
    g[antnr*2+ycor][xcor]+=val.conjugate()

  scipy.io.savemat(gainfilename, dict(g=g), oned_as='row')
  print "Stored timeslot",timeslot,"gains from", msname, "/",instrumentname,"as",gainfilename

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = "Extract gains from an instrument file, save in matlab format")
  parser.add_argument("msname", help="Name of the MS that contains data, model data and instrument table")
  parser.add_argument("-i", "--instrumentname", help="Name of instrument table", default="instrument")
  parser.add_argument("-t", "--timeslot", help="Time slot from gains and MS", type=int, default=0)
  parser.add_argument("-o", "--output", help="Save output in this output file", default="bbsgain.mat")

  args = parser.parse_args()

  gain2matlab(msname=args.msname,gainfilename=args.output,timeslot=args.timeslot,instrumentname=args.instrumentname)

