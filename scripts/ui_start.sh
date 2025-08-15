#!/bin/bash

# Get IP address
IP=`ip -4 a show $DEVICE | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | awk '$0 != "127.0.0.1" {print; exit}'`

# Start the UI configuration
uv run ui_backend.py $IP


