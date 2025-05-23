#!/usr/bin/env python3

import casacore.tables as pt
from os import path
import sys
from shutil import copytree
import argparse


def addsubtable(msfile, subtablefile, name=None, dry_run=False):
    """Adds an existing table as a subtable to another table
    The subtable is copied into the MS if it is not a subdirectory already"""

    subtablename = path.basename(subtablefile.rstrip("/"))

    if path.commonpath([msfile, subtablefile]) != path.commonpath([msfile]):
        print(f"Copying {subtablefile} into {path.join(msfile, subtablename)}")
        if not dry_run:
            copytree(subtablefile, path.join(msfile, subtablename))
        subtablefile = path.join(msfile, subtablename)

    t = pt.table(msfile, readonly=False, ack=False)
    sub = pt.table(subtablefile, ack=False)
    if not dry_run:
        t.putkeyword(subtablename, sub, makesubrecord=True)
    else:
        print(f"Would make {subtablename} a subtable of {msfile}")
    sub.close()

    if name is not None:
        if dry_run:
            print(f"Would set TELESCOPE_NAME={name} in {msfile}::OBSERVATION")
        else:
            pt.taql(f"UPDATE $t::OBSERVATION SET TELESCOPE_NAME='{name}'")

    t.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copy an existing table (e.g. PHASED_ARRAY) to another table as a subtable"
    )
    parser.add_argument("ms", help="Master measurement set")
    parser.add_argument("subtable", help="Subtable to add")
    parser.add_argument("-n", "--dry-run", help="Dry run", action="store_true")
    parser.add_argument("--name", help="Set telescope name", type=str)

    args = parser.parse_args()

    addsubtable(args.ms, args.subtable, dry_run=args.dry_run, name=args.name)
