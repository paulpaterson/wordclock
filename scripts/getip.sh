#!/bin/bash

# Return the IP address
if [ `which ip` ]; then
  echo `ip -4 a show $DEVICE | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | awk '$0 != "127.0.0.1" {print; exit}'`
else
  echo `ipconfig getifaddr en1`
fi

