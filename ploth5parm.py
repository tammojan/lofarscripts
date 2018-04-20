#!/usr/bin/env python
from __future__ import print_function

from casacore.tables import taql
from losoto.h5parm import h5parm
import numpy as np
from cursesmenu import SelectionMenu
import sys
from subprocess import call
from glob import glob

from matplotlib import pyplot as plt

def cursechoose(lst, title = "Make a selection"):
  nr = SelectionMenu.get_selection(lst, title = title)
  if nr == len(lst):
    "Exiting"
    sys.exit(0)
  else:
    return lst[nr], nr

files = glob('*.h5')
filename, __ = cursechoose(files, title = "Choose a file")

H = h5parm(filename)

solsetnames = H.getSolsets().keys()

if len(solsetnames)>1:
  solsetname, __ = cursechoose(solsetnames, title = "Select a solset")
else:
  solsetname = solsetnames[0]

parmkeys = H.getSoltabs(solsetname).keys()
parmkey, __ = cursechoose(parmkeys, title = "Select a parameter")

soltab = H.getSoltabs(solsetname)[parmkey]

antnames = list(soltab.ant)
antname, antnr = cursechoose(antnames, title = "Select a station")

vals = soltab.val[0, antnr, 0, :]
vals0 = soltab.val[0, 0, 0, :]

#plt.ylim([-0.5,0.5])
plt.plot(vals-vals0, '.', zorder=10)
plt.ylim([-0.125,0.125])
#plt.ylim([-3.15,3.15])
plt.xlim([0,len(vals)])
plt.ylabel(parmkey)
plt.xlabel("Time slot")
plt.title("Antenna " + antname)

# Make figure transparent, plot white
ax = plt.gca()
ax.set_zorder(2)
fig= plt.gcf()
fig.patch.set_alpha(0.0)

# Add flag bars
#ax2 = ax.twinx()
#flags=taql("select gntrue(FLAG) as nflag from /data/scratch/dijkema/tec/allsb/all_TC00.MS where mscal.ant1name()=='"+antname+"' group by TIME order by TIME").getcol('nflag')
#ax2.bar(np.arange(len(flags)), flags, 1.,color='r',edgecolor='r')
#ax2.set_zorder(1)
#ax2.set_ylim(4500,5000)
#ax.patch.set_alpha(0.0)
plt.xlim([0,len(vals)])

# Fit aspect ratio
fig.set_size_inches((8.7,5.5))

plt.savefig('myplot.pdf')

call('~/.iterm2/imgcat myplot.pdf', shell=True)
