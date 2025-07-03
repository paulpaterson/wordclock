#!/bin/bash

cd /home/paul/Workspace/wordclock

exit_status=2


until [ $exit_status -ne 2 ]; do
  source ./config.sh
  uv run terminal_version.py --button-pin 27 --mode-button-pin 25 --set-system-time 

  # Get the exit status of the last command
  exit_status=$?
done

echo "Finished"

