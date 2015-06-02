#!/usr/bin/env python

from pyrap.tables import table
import sys
import cmath
import argparse

def checkcols(msname, columnword, query=None):
  ''' Prints some value from all columns that contain columnword'''

  t=table(msname);
  if query is not None:
    print 'querying',query
    t1=t.query(query)
  elif len(t)>121:
    print 'Selecting rows 1,4,7,13,121'
    t1=t.selectrows(range(12)) #[1,4,7,13,121])
  elif len(t)<10:
    print 'Selecting all rows'
    t1=t;
  else:
    print 'Selecting first row'
    t1=t.selectrows([0]);

  modelcols = sorted([colname for colname in t1.colnames() if columnword in colname], key = lambda x: x.split('_')[2] if len(x.split('_'))>2 else x)

  if len(modelcols)==0:
    print 'No model columns found'
    return

  maxwidth = max([len(colname) for colname in modelcols])

  for row in t1:
    print str(row['ANTENNA1'])+', '+str(row['ANTENNA2'])
    for modelcol in modelcols:
      print ('{:>'+str(maxwidth)+'} : {:+02.8f} , {:+2.8f}, {:+.8f}').format(modelcol, float(abs(row[modelcol][2,0])), float(cmath.phase(row[modelcol][2,0])), complex(row[modelcol][2,0]))
    print '========='

if __name__ == '__main__':
  parser=argparse.ArgumentParser(description="Print some values for all MODEL_* columns of a MS")
  parser.add_argument("ms", help="Measurement set")
  parser.add_argument("-c", "--column", help="Column name (part of it) that should be shown", default="MODEL_")

  args=parser.parse_args()
 
  checkcols(args.ms, args.column)
