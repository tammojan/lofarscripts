#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Usage: showcols.MS. It will show the columns in a measurement set"
  else
    taql 'select * from '$1' limit 1' | sed -n '2p' | sed -e 's/[0-9]\+ selected columns:  //' | tr ' ' '\n'
fi
