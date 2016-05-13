#!/usr/bin/env python

from __future__ import print_function
import casacore.tables as pt
import numpy as np
from itertools import chain

import argparse

__version__ = "0.1"
__author__ = "Tammo Jan Dijkema, ASTRON"

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def flagsperant(msname):
    """
    Shows the amount of flagging per antenna and channel
    """

    t = pt.table(msname, readonly=False, ack=False)

    query = "SELECT TIME, ANTENNA%d AS ANT, NTRUES(GAGGR(FLAG),[0,2]) AS FLAG FROM $t GROUP BY ANTENNA%d, TIME"
    byant1 = pt.taql(query%(1,1));
    byant2 = pt.taql(query%(2,2));

    a=pt.taql("select * from $byant1")

    nAnt  = byant2[-1]["ANT"]+1
    nCh   = len(byant1[0]["FLAG"])
    nTime = byant1.nrows()/(nAnt-1)
    #print("nAnt",nAnt)
    #print("nCh",nCh)
    #print("nTime",nTime)
    hasautocorr = pt.taql("SELECT * FROM $t WHERE ANTENNA1==ANTENNA2").nrows()>0
    maxflags = (nAnt-1)*4;
    if hasautocorr:
      maxflags = nAnt * 4; # 4 polarizations
    print("maxflags",maxflags)

    times = pt.taql("SELECT DISTINCT TIME FROM $t").getcol("TIME");
    infodict={}
    for row in chain(byant1,byant2):
      for ch in range(nCh):
        infodict[(row["ANT"], row["TIME"], ch)] = infodict.get((row["ANT"], row["TIME"], ch), 0) + row["FLAG"][ch]

    timenum=0
    for time in times:
      print("Time {:>3}  :".format(timenum), end="")
      for ch in range(nCh):
        print("{:>4}".format(ch), end="")
      print()
      timenum+=1;
      for ant in range(nAnt):
        print("Antenna {:>2}:".format(ant), end="")
        for ch in range(nCh):
          if infodict.get((ant,time,ch), 0) > maxflags-3:
            print(color.RED,end="")
          print("{:>4}".format(infodict.get((ant,time,ch), 0)), end="")
          if infodict.get((ant,time,ch), 0) > maxflags-3:
            print(color.END,end="")
        print()
      print()

    t.close()

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=flagsperant.__doc__)
    parser.add_argument("ms", help="Measurement set")

    args = parser.parse_args()

    flagsperant(args.ms)
