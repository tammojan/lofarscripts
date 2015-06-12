#!/usr/bin/env python

import os
import argparse

parser = argparse.ArgumentParser(description = "Test which baselines match a baseline selection syntax")
parser.add_argument("msname",help="Name of the MS to test")
parser.add_argument("blselect", help="Baseline selection query (use single quotes around it)")

args = parser.parse_args()

command = "taql 'select [select NAME from ::ANTENNA][ANTENNA1] as ANTENNA1, [select NAME from ::ANTENNA][ANTENNA2] as ANTENNA2 "
command+= "from (select from " + args.msname +" where TIME in (select TIME from " + args.msname + " limit 1)) "
command+= "where mscal.baseline(\"" + args.blselect + "\")'"

print command
os.system(command)
