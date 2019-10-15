#!/usr/bin/env bash
export PATH="/home/tramsauer/bin/.anaconda3/bin:$PATH"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
date=$(date)
header="\n--------------------------\n"$date" executing rad_down:\n"
echo -e $header >> $DIR"/rad_down.log"
python $DIR/raddo.py &>> $DIR"/rad_down.log"
