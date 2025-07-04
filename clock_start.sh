#!/bin/bash

cd /home/paul/Workspace/wordclock

source .env/bin/activate

exit_status=2


until [ $exit_status -ne 2 ]; do
  source ./config.sh
  python terminal_version.py --button-pin 27 --mode-button-pin 25 --set-system-time 

  # Get the exit status of the last command
  exit_status=$?
done

echo "Finished"

