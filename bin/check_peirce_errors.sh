#!/bin/sh

/peirce/bin/peirce -extra-arg=-I/opt/ros/melodic/include/ /peirce/Peirce-vscode-api/$1 < /peirce/Peirce-vscode-api/inputs.txt 2>/dev/null | grep "Error Message:"
