#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description = "Show plots of the output of mem.py")
parser.add_argument("input", help="Input log file")
parser.add_argument("-1", "--onlymem", help="Show only memory, not CPU", action="store_true")

args = parser.parse_args()


log = np.rot90(np.loadtxt(args.input, skiprows=1))
x = np.arange(len(log[0]))

plt.figure(1)

if not args.onlymem:
  plt.subplot(211)

plt.plot(x, log[0])
plt.xlabel('Seconds since start')
plt.ylabel('Memory Usage [%]')

if not args.onlymem:
  plt.subplot(212)
  plt.plot(x, log[1])
  plt.xlabel('Seconds since start')
  plt.ylabel('CPU usage [%]')

plt.show()
