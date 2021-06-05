#!/bin/sh

/peirce/bin/peirce -extra-arg=-I/opt/ros/melodic/include/ $1 < /peirce/Peirce-vscode-api/blank_inputs.txt 2>/dev/null |  grep "Node Type :" | awk '{print $6}' | sed 's/.$//'
