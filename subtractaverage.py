#!/usr/bin/env python

from __future__ import print_function
import casacore.tables as pt
import numpy as np

import argparse

__version__ = "0.1"
__author__ = "Tammo Jan Dijkema, ASTRON"

def addcolumn(t, newcolname, likecolname):
    """
    Adds a column to a table if it does not exist.
    The new column will be like @likecolname@.
    """

    if newcolname in t.colnames():
        return  # Column already exists
    
    coldesc = t.getcoldesc(likecolname)
    coldesc['name'] = newcolname
    coldesc.pop('comment', None)
    t.addcols(coldesc)

def subtractmean(msname, inputcol, outputcol, timestep, freqstep):
    """
    Subtract mean value from the data in a measurement set.
    """

    t = pt.table(msname, readonly=False, ack=False)

    # Add output column if it does not exist
    addcolumn(t, outputcol, inputcol)

    # Add a temporary column for iterating over time chunks
    addcolumn(t, "TIMECHUNK", "ANTENNA1")

    nbl = pt.taql("select from $t where TIME in (select TIME from $t limit 1)").nrows()
    nfreq = t[0][inputcol].shape[0]

    pt.taql("update $t set TIMECHUNK = rownr()/($nbl*$timestep)") 

    for timechunk in t.iter("TIMECHUNK"):
        inputdata = timechunk.getcol(inputcol)
        outputdata = timechunk.getcol(outputcol)
        weights = timechunk.getcol("WEIGHT_SPECTRUM")
        flags = np.invert(timechunk.getcol("FLAG"))

        for f1 in range(0, nfreq, freqstep):
            f2 = f1 + freqstep
            for pol in range(0,4):
              outputdata[:,f1:f2,pol] = \
                inputdata[:,f1:f2,pol] - \
                np.average(inputdata[:,f1:f2,pol][flags[:,f1:f2,pol]],weights=weights[:,f1:f2,pol][flags[:,f1:f2,pol]])

        timechunk.putcol(outputcol, outputdata)

    t.removecols("TIMECHUNK")
    t.close()

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=subtractmean.__doc__)
    parser.add_argument("ms", help="Measurement set")
    parser.add_argument("-f", "--freqstep", help="Number of channels to average", default=1, type=int)
    parser.add_argument("-t", "--timestep", help="Number of timesteps to average", default=1, type=int)
    parser.add_argument("-i", "--inputcol", help="Input column (default: DATA)", default="DATA")
    parser.add_argument("-o", "--outputcol", help="Output column (default: same as input column)")

    args = parser.parse_args()

    if not args.outputcol:
        args.outputcol = args.inputcol

    if args.freqstep==1 and args.timestep==1 and False:
        print("Please specify timestep and freqstep.")
        print()
        parser.print_usage()
    else: 
        subtractmean(args.ms, args.inputcol, args.outputcol, args.timestep, args.freqstep)
        print("Subtracted (t=%d,f=%d) mean from %s, giving column %s."%(args.timestep, args.freqstep, args.inputcol, args.outputcol))
