#!/bin/bash

cd /home/paul/Workspace/wordclock
uv run data_update.py --interval 900 --weather  --homeassistant
