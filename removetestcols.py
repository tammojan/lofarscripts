#!/usr/bin/env python

from pyrap.tables import table
from sys import argv, stderr
import argparse

def removetestcols(msname, filterword='MODEL', force=False):
  t=table(msname,readonly=False)
  remlist=[c for c in t.colnames() if filterword in c]
  print >>stderr, "To remove:", remlist
  if not force:
	try:
	  dummyvar = raw_input("(press enter to continue, or Ctrl-C to abort)")
	except KeyboardInterrupt:
	  print
	  print "Keyboard interrupt caught, won't change",msname
	  t.close()
	  exit(1)

  t.removecols(remlist)
  print >>stderr, "Removed",remlist

if __name__=='__main__':
  try:
    deffile=open('curtest.txt','r')
    deffilename=deffile.read().strip()
    deffile.close()
  except:
    deffilename='test.MS' 

  parser=argparse.ArgumentParser(description="Remove test columns from a measurement set with pyrap")
  parser.add_argument('ms', help="Name of measurement set")
  parser.add_argument('-w', "--filterword", help="Word that is commond to column names to be removed", default='MODEL')
  parser.add_argument('-f', "--force", help="Force deletion, do not ask for confirmation", action="store_true")
  args=parser.parse_args()
  removetestcols(args.ms, args.filterword, force=args.force)
