#!/usr/bin/env python

from __future__ import print_function
from casacore.tables import taql
import casacore.tables as pt
import numpy
import numpy.random
import argparse

def addnoise(msname, colname_in, colname_out, sigma):
  ''' Adds noise to a measurement set '''
  query = 'update {msname} set {colname_out} = {colname_in} + '.format(
             msname=msname, colname_in=colname_in, colname_out=colname_out)
  #query += '{sigma:f} * sqrt(-2*log(rand()))*cos(2*pi()*rand())'.format(sigma=float(sigma));
  #print(query) # Blergh, I need an array of random numbers or so
  #taql(query) 
  t = pt.table(msname, readonly=False, ack=False)
  datashape = t[0][colname_in].shape
  for rownr in range(t.nrows()):
    t.putcell(colname_out, rownr, t.getcell(colname_in, rownr) + 
                    sigma * numpy.random.randn(*datashape) +
                    (0+1j) * sigma * numpy.random.randn(*datashape))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = "Add noise to a data column in a MS")
  parser.add_argument("msname", help="Measurement set to alter")
  parser.add_argument("colname_in", help="Data from which to take the ideal data")
  parser.add_argument("colname_out", help="Data to which to store the result")
  parser.add_argument("sigma", help="Standard deviation of noise to add", type=float)
 
  args = parser.parse_args()

  addnoise(args.msname, args.colname_in, args.colname_out, args.sigma)
