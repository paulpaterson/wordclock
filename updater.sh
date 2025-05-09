#!/bin/bash

cd /home/paul/Workspace/wordclock
source .env/bin/activate
python data_update.py --interval 600 --weather
