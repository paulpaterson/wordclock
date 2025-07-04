#!/bin/bash


exit_status=2


until [ $exit_status -ne 2 ]; do
  source ./config.sh
  source ./local_config.sh
  uv run terminal_version.py --set-system-time

  # Get the exit status of the last command
  exit_status=$?
done

echo "Finished"

