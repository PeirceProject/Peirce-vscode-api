#!/bin/sh

echo 6 | /peirce/bin/peirce /api/$1 2>/dev/null | grep -Poe "Begin: line [0-9]*, column [0-9]*\tEnd: line [0-9]*, column [0-9]*"
