#!/usr/bin/env bash
export PATH="/home/tramsauer/bin/.anaconda3/bin:$PATH"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
date=$(date)
header="\n--------------------------\n"$date" executing sort_tars:\n"
echo -e $header >> $DIR"/rad_down.log"
python ~/Code/toms-code/Radolan_Download/sort_tars.py &>> $DIR"/rad_down.log"
