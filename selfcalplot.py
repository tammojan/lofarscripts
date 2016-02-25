#!/usr/bin/env python
import pyfits
import astropy.io.fits
import aplpy
import re
from math import sqrt
import glob
import argparse
import os
import matplotlib.pyplot as plt

def makepng(name, directory, bw=40, obstime=5, drawcolorbar=False):
    allfits=glob.glob(os.path.join(directory, '**image??.image.fits'))
    prog = re.compile(r".*facet_patch_([0-9]+)_.*")
    facets=set([prog.match(onefits).group(1) for onefits in allfits])

    for facet in facets:
        filenames=sorted(glob.glob(os.path.join(directory, '*facet_patch_'+facet+'*image??.image.fits')))
        print "Filenames:", [filename[-18:-10] for filename in filenames]
        if len(filenames)!=5:
            print "Error: expecting exactly 5 files matching *image??.image.fits"
            continue
    
        if drawcolorbar:
            w=0.18
        else:
            w=0.2
        fig=plt.figure(figsize=(15,15*w))
    
        imagenoise = 5E-3*sqrt(bw/40.)*sqrt(obstime/5.)
    
        if drawcolorbar:
            f=astropy.io.fits.open(filename)
            a=aplpy.FITSFigure(f, figure=fig, subplot=[w*5+0.02,0,0.3,1])
            a.show_colorscale(vmax=10*imagenoise, vmin=-3*imagenoise)
            a.add_colorbar()
            a.colorbar.set_location("left")
            a.colorbar.set_pad(0.5)
            a.tick_labels.hide()
            a.axis_labels.hide()
            a.set_tick_size(0)
    
        for i,filename in enumerate(filenames):
            f=astropy.io.fits.open(filename)
            a=aplpy.FITSFigure(f, figure=fig, subplot=[w*i,0,w,1])
            a.show_colorscale(vmax=10*imagenoise, vmin=-3*imagenoise)
            a.tick_labels.hide()
            a.axis_labels.hide()
    
        outname=name+"-facet_"+facet+".png"
        print "Saving to "+outname
        plt.savefig(outname, transparent=True, dpi=100)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help="Name of output file (without .png)")
    parser.add_argument('directory', help="Directory with fits images")
    parser.add_argument('--bw', help="Bandwidth (number of bands), to set color bar (default 40)", default=40)
    parser.add_argument('--obstime', help="Observing time in hours, to set color bar (default 5)", default=5)
    parser.add_argument('--drawcolorbar', help="Draw colorbar (default false)", action='store_true', default=False)
    args=parser.parse_args()

    makepng(args.name, args.directory, args.bw, args.obstime, args.drawcolorbar)
