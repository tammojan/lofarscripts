#!/usr/bin/env python

from pyrap.tables import table
from os import path
import sys
from shutil import copytree
import argparse

def addsubtable(msfile, subtablefile, subtablename=None):
  ''' Adds an existing table as a subtable to another table'''
  ''' The subtable is copied into the MS if necessary '''

  if subtablename is None:
    subtablename=path.basename(subtablefile.rstrip('/'))
  else:
    if subtablefile.startswith(msfile):
      print "Error: when the subtable is already in the MS, don't specify a new name for it"
      sys.exit(1)

  if not subtablefile.startswith(msfile):
    print "Copying", subtablefile, " into", path.join(msfile, subtablename) 
    copytree(subtablefile, path.join(msfile, subtablename))
    subtablefile=path.join(msfile, subtablename)

  t=table(msfile, readonly=False, ack=False)
  sub=table(subtablefile, ack=False)
  t.putkeyword(subtablename, sub, makesubrecord=True)
  sub.close()
  t.close()

if __name__ == '__main__':
  parser=argparse.ArgumentParser(description="Adds an existing table (e.g. instrument) to another table")
  parser.add_argument("ms", help="Master measurement set")
  parser.add_argument("subtable", help="Subtable to add")
  parser.add_argument("-s", "--subtablename", help="Name of subtable (defaults to its filename)", default=None)
  
  args=parser.parse_args()

  addsubtable(args.ms, args.subtable, args.subtablename) 
