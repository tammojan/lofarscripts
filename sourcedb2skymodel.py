#!/usr/bin/env python

''' Convert a sourcedb back into a .skymodel '''
import os
import sys
import subprocess
import re
from collections import deque

sourcedb=sys.argv[1]
print "# (Name, Type, Ra, Dec, I, ReferenceFrequency, SpectralIndex='[]', MajorAxis, MinorAxis, Orientation) = format"

def sourcedb2sourcelist(sourcedbfile):
  sourcetypes=['POINT','GAUSSIAN']
  sources=[]
  FNULL = open(os.devnull, 'w')
  showsourcedboutput=subprocess.check_output(['showsourcedb','in='+sourcedb,'mode=source'],stderr=FNULL)
  lq=deque(showsourcedboutput.split('\n'))
  while len(lq)>0:
   source={}
   line=lq.popleft()
   if line[0:2]=='  ' and line[3]!=' ':
    #  17:34:06.929 +059.15.33.300 J2000  1734.1+5915 0  iquv=(2.8455,0,0,0)
    (source['ra'],source['dec'],j2000,bla,source['name'],sourcetypeid,bla,iquv)=line.strip().split(' ')
    source['sourcetype']=sourcetypes[int(sourcetypeid)]
    (source['i'],q,u,v)=iquv.split('=')[1].strip('(').strip(')').split(',')
    source['major'],source['minor'],source['orientation']=('','','')
    if source['sourcetype']=='GAUSSIAN':
      gaussianline=lq.popleft().strip()
      #major=43.8 arcsec  minor=31.9 arcsec  orientation=3.6 deg
      m = re.match('major=(.*) arcsec  minor=(.*) arcsec  orientation=(.*) deg',gaussianline)
      (source['major'],source['minor'],source['orientation'])=(m.group(1),m.group(2),m.group(3))
    spline=lq.popleft().strip()
    #spindex=[-0.7691,-0.1228] reffreq=60 MHz
    m = re.match('spindex=(.*) reffreq=(.*) MHz', spline)
    source['spindex']=m.group(1)
    source['reffreq']=int(m.group(2))*1e6
    sources=sources+[source]
  return sources

def sourcelist2skymodel(sources):
  for source in sources:
    print '{0}, {1}, {2}, {3}, {4}, {5:.0e}, {6}'.format(source['name'], 
                                                         source['sourcetype'], 
                                                         source['ra'],
                                                         source['dec'], 
                                                         source['i'], 
                                                         source['reffreq'],
                                                         source['spindex']),
    if source['sourcetype']=='GAUSSIAN':
      print ', {0}, {1}, {2}'.format(source['major'], source['minor'], source['orientation'])
    else:
      print ''

if __name__=="__main__"
  import argparse

  parser = argparse.ArgumentParser(description = "Converts a sourcedb into a skymodel (currently depends on a hack in the lofar tree)")
  parser.add_argument("sourcedb", help="Sourcedb to convert")
  parser.add_argument("--sort","-s", help="Sort the sources in decreasing intensity", action="store_true")
  parser.add_argument("--rename","-r", help="Rename the sources to their index", action="store_true")
  args=parser.parse_args()

  sources=sourcedb2sourcelist(args.sourcedb)
  
  if args.sort: 
    sources=sorted(sources,key=lambda student: student['i'],reverse=True)

  if args.rename:
    teller=0
    for source in sources:
      teller+=1
      source['name']=str(teller)

  sourcelist2skymodel(sources)
