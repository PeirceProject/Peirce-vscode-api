#!/bin/sh

/peirce/bin/peirce -extra-arg=-I/opt/ros/melodic/include/ /api/$1 < /api/inputs.txt 2>/dev/null | grep "Existing Interpretation:"
