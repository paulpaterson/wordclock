#!/bin/bash

# Get IP address
IP=`ip -4 a show $DEVICE | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | sed -n '$p'`

# Start the UI configuration
uv run ui_backend.py $IP


