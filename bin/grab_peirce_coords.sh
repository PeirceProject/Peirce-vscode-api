#!/bin/sh

/peirce/bin/peirce -extra-arg=-I/opt/ros/melodic/include/ /api/$1 < /api/blank_inputs.txt 2>/dev/null |  grep -Poe "Begin: line [0-9]*, column [0-9]*\tEnd: line [0-9]*, column [0-9]*"
