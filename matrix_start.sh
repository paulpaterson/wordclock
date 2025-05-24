#!/bin/bash

source .env/bin/activate
python matrix_display.py --leds --interval 0.2  --config configurations.sand_sim
