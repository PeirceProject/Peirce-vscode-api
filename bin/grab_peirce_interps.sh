#!/bin/sh

echo 6 | /peirce/bin/peirce /api/$1 2>/dev/null | grep "Existing Interpretation:"
