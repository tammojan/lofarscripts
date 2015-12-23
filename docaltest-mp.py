#!/usr/bin/env python

import pyrap.tables as pt
import lofar.parmdb as lp
import os
import argparse
from pylab import *
import matplotlib.pyplot as plt
from numpy import *
import subprocess

import multiprocessing as mp

def oscsystem(cmd):
  retval=os.system(cmd)
  #try:
  #  subprocess.check_output(cmd.split(' '), stderr=subprocess.STDOUT)
  #except subprocess.CalledProcessError as e:
  #  print 'oei:', e
  #  raise
  #processname=mp.current_process().name
  if retval!=0:
    #raise Exception('Exception thrown in', processname)
    raise Exception('oei:', cmd, 'retval:', retval)

def doaverage(ms,skymod):
  ''' Perform flagging and averaging. Skymod is only used for smart demixing '''
  processname=mp.current_process().name
  newms = ms.split('.MS')[0]+'.dppp.MS'
  dpppparset = """
     msin="""+ms+"""
     msout="""+newms+"""
     msout.overwrite=true
     showprogress=false
     showtimings=false
     showcounts=false
     steps=[preflag,badst,flagedge,aoflag,demix,filter]
     preflag.baseline='*&&&'
     flagedge.type=preflagger
     flagedge.chan=[0,1,30,31]
     badst.type=preflagger
     badst.baseline='CS004HBA*;RS503*'
     demix.type=smartdemix
     demix.demixtimestep=90
     demix.demixfreqstep=32
     demix.timestep=5
     demix.freqstep=32
     demix.ateam.skymodel="Ateamhighresdemix.sourcedb"
     demix.estimate.skymodel="Ateam-lowresdemix.sourcedb"
     demix.target.skymodel="""+skymod+"""
     demix.instrumentmodel="demix_instrument_"""+processname+""""
     demix.sources=[]
     filter.baseline='!CS013*&&*'
     filter.remove=True
  """
  oscsystem('NDPPP '+dpppparset.replace('\n',' '))
  oscsystem('rm -rf demix_instrument_%s'%processname)
  return newms

def getbadstations(parmdbname,cutoff,antnames):
  ''' Flag bad stations based on amplitudes in a parmdb. 
      Returns a semicolon separated list, to be used in msselect'''
  sl = set([])
  p = lp.parmdb(parmdbname)
  dv = p.getDefValues('*Ampl*')
  for val in dv:
    if dv[val][0][0] < cutoff:
      sl.add(val.split(':')[-1])
  outstring = ''
  for s in sl:
    if s in antnames:
      outstring = outstring + '!' + s + ';'
  return outstring[:-1]

def docal(ms,smname,getinst):
  ''' Do calibration. If getinst is True, do primary calibration. '''
  processname=mp.current_process().name
  if getinst:
    #oscsystem('./docalibratestandalone -f %s bbscal.parset %s'%(ms,smname))
    oscsystem('./dodppp showprogress=false showcounts=false msin='+ms+' msout=. steps=[gaincal] gaincal.caltype=diagonal gaincal.sourcedb='+smname+'.sourcedb gaincal.usebeammodel=true')
    oscsystem('parmexportcal in=%s/instrument out=%s_tmpinst zerophase=True type=polar'%(ms,processname))
    newms = ms.split('.MS')[0]+'.prical.MS'
    newms2 = ms.split('.MS')[0]+'.prical.sel.MS'
  else:
    newms = ms.split('.MS')[0]+'.seccal.MS'
    newms2 = ms.split('.MS')[0]+'.seccal.sel.MS'
  # Apply amplitude solutions, write to CORRECTED_DATA, do phase calibration
  oscsystem(("""./dodppp
     msin="""+ms+"""
     msout=.
     showcounts=flase
     showprogress=false
     msout.datacolumn=CORRECTED_DATA
     steps=[applycal,gaincal]
     applycal.parmdb="""+processname+"""_tmpinst
     gaincal.sourcedb="""+smname+""".sourcedb
     gaincal.caltype=phaseonly
     gaincal.parmdb="""+processname+"""_tmpinst2
     gaincal.usebeammodel=true""").replace('\n',' ')
  )
  #oscsystem('./docalibratestandalone --replace-sourcedb --parmdb %s_tmpinst %s bbsphasecal.parset %s'%(processname,ms,smname))
  # Apply phase calibration, write to CORRECTED_DATA
  oscsystem(("""./dodppp
     msin="""+ms+"""
     msout=.
     msin.datacolumn=CORRECTED_DATA
     msout.datacolumn=CORRECTED_DATA
     steps=[applycal,aoflagger]
     applycal.parmdb="""+processname+"""_tmpinst2""").replace('\n',' ')
  )
  #oscsystem('NDPPP msin=%s msout=%s msout.overwrite=true showcounts=false showprogress=false msin.datacolumn=CORRECTED_DATA steps=[aoflagger]'%(ms,newms))
  tant = pt.table('%s/ANTENNA'%newms,readonly=True,ack=False)
  antnames = tant.getcol('NAME')
  bs = getbadstations('%s_tmpinst'%processname,0.01,antnames)
  if bs == '':
    return newms
  else:
    oscsystem('msselect in=%s out=%s deep=true baseline="%s"'%(newms,newms2,bs))
    return newms2

def uvflux(ms,column,baseline):
  t = pt.table(ms,readonly=True,ack=False)
  stats = pt.taql("select gstddev(SUMMED) as STDVALS, gmean(SUMMED) as MEANVALS, gcount(SUMMED) as NVALS from (select gmean(mean(0.5*(abs(%s[,0])+abs(%s[,3])))) as SUMMED from $t where (mscal.baseline('%s') and any(FLAG)!=True) GROUP BY TIME)"%(column,column,baseline))
  meanvals = stats.getcol('MEANVALS')[0]
  nvals = stats.getcol('NVALS')[0]
  stdvals = stats.getcol('STDVALS')[0]/sqrt(nvals)
  print ms,': from',nvals,'time samples, flux is',meanvals,'+/-',stdvals,'(%.2f%% fractional uncertainty)'%((stdvals/meanvals)*100.)
  return meanvals,stdvals

def sourcespec(name,infr):
  fr = infr/150. # reference frequency
  if name == '3C196':
    a0,a1,a2,a3,a4 = 83.084,-0.699,-0.110,0.,0.
  elif name == '3C295':
    a0,a1,a2,a3,a4 = 97.763,-0.582,-0.298,0.583,-0.363
  elif name == '3C380':
    a0,a1,a2,a3,a4 = 77.352,-0.767,0.,0.,0.
  elif name == '3C286':
    a0,a1,a2,a3,a4 = 27.477,-0.158,0.032,-0.180,0.
  else:
    a0,a1,a2,a3,a4 = 100.,-0.7,0.,0.,0.
  logs = log10(a0) + a1*log10(fr) + a2*(log10(fr)**2) + a3*(log10(fr)**3) + a4*(log10(fr)**4)
  return 10.**logs

def getfinalmsname(ms,lev):
  if os.path.isdir(ms.split('.MS')[0]+'.dppp.%scal.sel.MS'%lev):
    return ms.split('.MS')[0]+'.dppp.%scal.sel.MS'%lev
  else:
    return ms.split('.MS')[0]+'.dppp.%scal.MS'%lev

def threadmain((args, i)):
    processname=mp.current_process().name
    calname = args.calskymod[:5]
    tarname = args.tarskymod[:5]

    cal_outf = open(calname+'_prical_stats_%d.txt'%i,'w')
    pritar_outf = open(tarname+'_prical_stats_%d.txt'%i,'w')
    sectar_outf = open(tarname+'_seccal_stats_%d.txt'%i,'w')

    calms = args.calmsid+'_SB%03d_uv.dppp.MS'%i
    tarms = args.tarmsid+'_SB%03d_uv.dppp.MS'%i
    if args.shortcut:
      finalcalms = getfinalmsname(calms,'pri')
      checktarms = getfinalmsname(tarms,'pri')
      finaltarms = getfinalmsname(tarms,'sec')
    else:
      oscsystem('cp -r %s/%s .'%(args.datadir,calms))
      oscsystem('cp -r %s/%s .'%(args.datadir,tarms))
      newcalms = doaverage(calms,calname+'.sourcedb')
      newtarms = doaverage(tarms,tarname+'.sourcedb')
      finalcalms = docal(newcalms,args.calskymod,True)
      finaltarms = docal(newtarms,args.tarskymod,False)
      oscsystem('rm -rf %s_tmpinst'%processname)
      checktarms = docal(newtarms,args.tarskymod,True)
      oscsystem('rm -rf %s_tmpinst'%processname)

    calprimean,calpristd = uvflux(finalcalms,'DATA',args.baseline)
    tarsecmean,tarsecstd = uvflux(finaltarms,'DATA',args.baseline)
    tarprimean,tarpristd = uvflux(checktarms,'DATA',args.baseline)
    tsw = pt.table('%s/SPECTRAL_WINDOW'%finalcalms,readonly=True,ack=False)
    freq = tsw.getcol('CHAN_FREQ')[0][0]
    print >>cal_outf, freq, calprimean,calpristd
    print >>pritar_outf, freq, tarprimean,tarpristd
    print >>sectar_outf, freq, tarsecmean,tarsecstd

    cal_outf.close()
    pritar_outf.close()
    sectar_outf.close()

def makeplot(ax, title, ymin, ymax):
  #ax.set_xscale('log')
  ax.set_yscale('log')
  ax.set_xlim(110.,190.)
  ax.set_ylim(ymin,ymax)
  #ax.set_xticks(arange(110.,191.,10.0))
  if ymax>=200:
    ax.set_yticks([50,60,70,80,90,100,125,150,175,200])
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
  ax.set_xlabel('Frequency (MHz)')
  ax.set_ylabel('Flux density (Jy)')
  ax.set_title(title)
  

def main(args):
  freqs=range(0,380,args.delta)
  argsfreqs=[(args,freq) for freq in freqs]

  calname = args.calskymod[:5]
  tarname = args.tarskymod[:5]

  if not args.shortercut:
    pool = mp.Pool(int(args.numthreads)) # number of concurrent frequencies
    try:
      if args.numthreads==1:
        map(threadmain, argsfreqs)
      else:
        pool.map(threadmain, argsfreqs)
    except Exception as e:
      print e
    oscsystem('cat %s_prical_stats_*.txt > %s_prical_stats.txt'%(calname,calname))
    oscsystem('cat %s_prical_stats_*.txt > %s_prical_stats.txt'%(tarname,tarname))
    oscsystem('cat %s_seccal_stats_*.txt > %s_seccal_stats.txt'%(tarname,tarname))

  caldata = loadtxt(calname+'_prical_stats.txt')
  pritardata = loadtxt(tarname+'_prical_stats.txt')
  sectardata = loadtxt(tarname+'_seccal_stats.txt')

  xax=arange(110.,190.1,1.)

  fig, (ax0, ax1, ax2) = plt.subplots(1,3,figsize=(24,6))

  makeplot(ax0,'Primary calibrator (%s), direct calibration'%calname,40.,210.)
  ax0.plot(xax,sourcespec(calname,xax),'k--')
  ax0.errorbar(caldata[:,0]/1.e6,caldata[:,1],yerr=caldata[:,2],marker='o',linestyle='none')

  secymin = float(args.yaxislim.split(',')[0])
  secymax = float(args.yaxislim.split(',')[1])

  makeplot(ax1,'Secondary calibrator (%s), direct calibration'%tarname,secymin,secymax)
  ax1.plot(xax,sourcespec(tarname,xax),'k--')
  ax1.errorbar(pritardata[:,0]/1.e6,pritardata[:,1],yerr=pritardata[:,2],marker='o',linestyle='none')

  makeplot(ax2,'Secondary calibrator (%s), transferred calibration'%tarname,secymin,secymax)
  ax2.plot(xax,sourcespec(tarname,xax),'k--')
  ax2.errorbar(sectardata[:,0]/1.e6,sectardata[:,1],yerr=sectardata[:,2],marker='o',linestyle='none',label='old model')
  #ax2.legend()

  savefig(args.plot,bbox_inches='tight')
  if args.onscreen: show()

ap = argparse.ArgumentParser()
ap.add_argument('tarmsid',help='Target cal MS ID e.g. L245285')
ap.add_argument('tarskymod',help='Target sky model')
ap.add_argument('calmsid',help='Master cal MS ID e.g. L245291')
ap.add_argument('calskymod',help='Calibrator sky model')
ap.add_argument('-d','--delta',help='Spacing between MSs to process [default 10]',default=10,type=int)
ap.add_argument('-b','--baseline',help='Baseline restriction for flux determination (only!) [default "5000m~10000m"]',default='5000m~10000m')
ap.add_argument('-p','--plot',help='Output plot name [default "caltest.png"]',default='caltest.png')
ap.add_argument('-D','--datadir',help='Directory with the original data [default ..]',default='..')
ap.add_argument('-t','--numthreads',help='number of threads to use [default=1]',default=1)
ap.add_argument('-s','--shortcut',help='Shortcut and jump directly to plot? [default False]',action='store_true',default=False)
ap.add_argument('-S','--shortercut',help="Only plot, read data from text file [default False]",default=False,action='store_true')
ap.add_argument('-o','--onscreen',help='Display plot onscreen? [default False]',default=False,action='store_true')
ap.add_argument('-y','--yaxislim',help='Yaxis limits for target flux scale plot [default 40,210]',default='40,210')
args = ap.parse_args()
main(args)

