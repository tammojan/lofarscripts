#!/usr/bin/env python

import pylab
import numpy
import pyrap.tables as pt
import pyrap.images as pim
import os
import lofar.stationresponse as lsr
import time
import pyfits
import pywcs
import sys

import argparse
import multiprocessing as mp

def pointsgenerator():
 for i in range(51,52): #range(0,len(xvals),ds):
   for j in range(75,76): #range(0,len(xvals),ds):
     yield i,j

def mkcube(freqfits,outfits):
  ''' Put the data of all files in freqfits into one big cube outfis '''
  h = pyfits.open(freqfits[0])
  hdr = h[0].header
  nx = hdr['NAXIS1']
  ny = hdr['NAXIS2']
  nz = len(freqfits)
  outcube = numpy.zeros((nz,ny,nx))

  for i in range(nz):
    h = pyfits.open(freqfits[i])
    outcube[i,:,:]=h[0].data

  hdu = pyfits.PrimaryHDU(data=outcube, header=hdr)
  hdu.writeto(outfits,clobber=True)

def main((frequency, msname, minst, maxst)): # Arguments as a tuple to make threading easier
  assert maxst+1 > minst
  
  # Set frequency of the MS to the specified frequency
  freqmhz = int(frequency/1.e6)
  print frequency,freqmhz
  t = pt.table(msname+'/SPECTRAL_WINDOW',readonly=False,ack=True)
  t.putcol('REF_FREQUENCY',numpy.array([frequency]))
  t.putcol('CHAN_FREQ',numpy.array([[frequency]]))
  t.close()
  
  t = pt.table(msname,ack=False)
  timecol = t.getcol('TIME')
  msreftime = min(timecol)
  print 'time reference', msreftime
  JD = msreftime/3600./24. + 2400000.5
  print 'MS JD', JD
  
  # makeresponseimage abs=true frames=1 ms=freq00.MS size=350 cellsize=1200arcsec stations=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59
  
  def azel2radec(az,el,lon,lat,JD):
  	#JD = 2456788.5279360712
  	#lon = 6.869883*numpy.pi/180.
  	#lat = 52.915111*numpy.pi/180.
  	T_UT1 = (JD-2451545.)/36525.
  	ThetaGMST = 67310.54841 + (876600.*3600. + 8640184.812866)*T_UT1 + .093104*T_UT1**2 - 6.2e-6*T_UT1**3
  	ThetaGMST = (ThetaGMST%(86400.*(ThetaGMST/abs(ThetaGMST)))/240.)%360.
  	ThetaLST = ThetaGMST*numpy.pi/180. + lon
  	DEC = numpy.arcsin(numpy.sin(el)*numpy.sin(lat)+numpy.cos(el)*numpy.cos(lat)*numpy.cos(az))
  	LHA = numpy.arctan2(-numpy.sin(az)*numpy.cos(el)/numpy.cos(DEC),(numpy.sin(el)-numpy.sin(DEC)*numpy.sin(lat))/(numpy.cos(DEC)*numpy.cos(lat)))
  	RA = (ThetaLST-LHA)%(2.*numpy.pi)
  	return RA,DEC
  
  hs = 100.
  ds = 1 # downsample, ** was 2 **
  
  xvals = numpy.arange(-hs,hs+1.)
  X,Y = numpy.meshgrid(xvals,xvals)
  R=numpy.hypot(X,Y)
  
  #w = wcs.WCS(naxes=2)
  #w.wcs.crpix=[151,151]
  #w.wcs.cdelt=array([165./301.,165./301.])
  #w.wcs.crval=[0.,90.]
  #w.wcs.ctype=['RA---ZEA','DEC--ZEA']
  h = pyfits.open('wcs_azimuth_201.fits')
  w = pywcs.WCS(h[0].header)
  
  els = numpy.zeros(R.shape)
  azs = numpy.zeros(R.shape)
  for i in range(R.shape[0]):
   for j in range(R.shape[1]):
    azel = w.wcs_pix2sky([[i,j]],0)
    if azel[0][1]<0.:
      els[i,j]=numpy.nan
      azs[i,j]=numpy.nan
    elif ((i-hs)**2+(j-hs)**2)**0.5 > 1.2*hs:
      els[i,j]=numpy.nan
      azs[i,j]=numpy.nan
    else:
      els[i,j]=azel[0][1]*numpy.pi/180.
      azs[i,j]=azel[0][0]*numpy.pi/180.
  
  
  t = pt.table(msname+'/ANTENNA',ack=False)
  stcol = t.getcol('NAME')
  #stations = range(len(stcol))
  stations = range(minst,maxst+1)
  print len(stations), 'stations'
  
  beamintmap = numpy.zeros((2,len(stations),len(range(0,len(xvals),ds)),len(range(0,len(xvals),ds))))
  beamtmpmap = numpy.zeros((2,len(stations),len(xvals),len(xvals)))
  azmap = numpy.zeros((len(range(0,len(xvals),ds)),len(range(0,len(xvals),ds))))
  elmap = numpy.zeros((len(range(0,len(xvals),ds)),len(range(0,len(xvals),ds))))
  
  sr = lsr.stationresponse(msname, useElementResponse=True)
  
  stll = {}
  for line in open('stations_positions.txt'):
   sline = line.split()
   stll[sline[0]]=[float(sline[2])*numpy.pi/180.,float(sline[3])*numpy.pi/180.] # lon, lat
  
  t = time.time()
  # directionmap contains itrf directions for every x,y point
  directionmap=numpy.zeros((len(xvals),len(xvals),3))
  
  evals=0
  for ss in range(len(stations)):
   ra,dec=azel2radec(azs,els,stll[stcol[stations[ss]][:5]][0],stll[stcol[stations[ss]][:5]][1],JD)
   decisnan=numpy.isnan(dec)
  
   directionmap*=0.;
   for i,j in pointsgenerator():
       if not decisnan[i,j]:
         sr.setDirection(ra[i,j],dec[i,j])
         tmpdirection=sr.getDirection(msreftime)
         directionmap[i,j,:]=tmpdirection
  
   for i,j in pointsgenerator():
     azmap[i/ds,j/ds]=azs[i,j]
     elmap[i/ds,j/ds]=els[i,j]
     #print dec[i,j]
     #exit()
     lenxvals=len(xvals)
     tmpra=0.
     tmpdec=0.
  
     if not numpy.isnan(dec[i,j]):
      thisra=ra[i,j]
      thisdec=dec[i,j]
      sr.setRefDelay(thisra,thisdec)
      sr.setRefTile(thisra,thisdec)
      refdelay=sr.getRefDelay(msreftime)
      reftile=sr.getRefTile(msreftime)
      beamtmpmap*=0.
      for x in xrange(lenxvals):
       for y in xrange(lenxvals):
        if not decisnan[x,y]:
         #tmpra = ra[x,y]
         #tmpdec = dec[x,y]
         #sr.setDirection(tmpra,tmpdec)
         #mydirection=sr.getDirection(msreftime)
         mydirection=directionmap[x,y]
         bmj=sr.evaluateFreqITRF(msreftime,stations[ss],frequency,mydirection,refdelay,reftile)
         #bmj1=sr.evaluateFreq(msreftime,stations[ss],frequency)
         evals+=1
         #beamtmpmap[ss,x,y]=numpy.sum(numpy.abs(bmj))
         beamtmpmap[0,ss,x,y]=numpy.sqrt(numpy.abs(bmj[0,0])**2+numpy.abs(bmj[0,1])**2)
         beamtmpmap[1,ss,x,y]=numpy.sqrt(numpy.abs(bmj[1,1])**2+numpy.abs(bmj[1,0])**2)
     beamintmap[0,ss,j/ds,i/ds]=numpy.sum(beamtmpmap[0,ss,:,:])#*cosel)
     beamintmap[1,ss,j/ds,i/ds]=numpy.sum(beamtmpmap[1,ss,:,:])#*cosel)
  
   print ss,'/',len(stations),'-',i/ds,'/',len(range(0,len(xvals),ds)),':',int(time.time()-t),'sec elapsed so far,',evals,'beam evaluations'
  
  header = h[0].header
  #header['CRPIX1']=51.
  #header['CRPIX2']=51.
  #pixsize = header['CDELT1']
  #pixsize *= 2.
  #header['CDELT1']=pixsize
  #header['CDELT2']=pixsize
  for stationnr in range(minst, maxst+1):
    stationname=stcol[stationnr]
    hdu = pyfits.PrimaryHDU(header=header,data=beamintmap[0,stationnr-minst,])
    hdu.writeto('beamcubexx-%s-%dMHz.fits'%(stationname,freqmhz),clobber=True)
    hdu = pyfits.PrimaryHDU(header=header,data=beamintmap[1,stationnr-minst,])
    hdu.writeto('beamcubeyy-%s-%dMHz.fits'%(stationname,freqmhz),clobber=True)
  #hdu = pyfits.PrimaryHDU(elmap)
  #hdu.writeto('beamelmap-all-%dMHz.fits'%freqmhz,clobber=True)
  #hdu = pyfits.PrimaryHDU(azmap)
  #hdu.writeto('beamazmap-all-%dMHz.fits'%freqmhz,clobber=True)

 
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = """Make a beam cube all frequencies 
and a number of stations. It needs a list of files editme01.ms ... editme20.ms""")
  parser.add_argument("minst", help="First station index", type=int)
  parser.add_argument("maxst", help="Last station index (inclusive)", type=int)
  
  args=parser.parse_args()

  frequencies=range(100.e6, 200.e6, 5.e6)
  allargs=[]
  for i in range(len(frequencies)):
    allargs+=[(frequencies[i], "editme%02d.ms"%i,args.minst, args.maxst)]

  pool = mp.Pool(len(frequencies))
 
  t = pt.table('editme00.ms/ANTENNA',ack=False)
  stcol = t.getcol('NAME')
  stationnames=[stcol[stationnr] for stationnr in range(args.minst, args.maxst+1)]
 
  pool.map(main, allargs)

  for pol in ["xx","yy"]:
    for stationname in stationnames:
      outfiles=["beamcube%s-%s-%dMHz.fits"%(pol,stationname,int(frequency/1.e6)) for frequency in frequencies]
      mkcube(outfiles,"beamcube%s-%s.fits"%(pol,stationname))
