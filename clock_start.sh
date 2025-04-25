#!/bin/bash

cd /home/paul/Workspace/wordclock
source .env/bin/activate
python terminal_version.py --mode 16x16 --light-mode real --interval 10 --baud-rate 1000 --show-it-is --light-color 255 255 0


