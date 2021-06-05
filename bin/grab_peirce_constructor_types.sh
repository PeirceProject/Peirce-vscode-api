#!/bin/sh

/peirce/bin/peirce -extra-arg=-I/opt/ros/melodic/include/ $1 < /peirce/Peirce-vscode-api/constructor_inputs.txt 2>/dev/null |  grep "Type :" | awk '{print $6}' | sed 's/.$//'
