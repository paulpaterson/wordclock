#!/bin/bash

# This script is used to configure the Raspberry PI machine to be able to run the software
# Run it *once* before running the software

set -e

# BOOT Behaviour

printf "Setting machine to boot to command line ... "
sudo raspi-config nonint do_boot_behaviour B1
printf "Done!\n"

# SSH logging in - disable if you don't want this

printf "Turning on SSH ... "
sudo raspi-config nonint do_ssh 0
printf "Done!\n"
printf "You can ssh into this machine now at address: "
printf "`ip -4 a show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`\n"

# SPI Interface - needed for the matrix control

printf "Turning on the SPI interface ..."
sudo raspi-config nonint do_spi 0
printf "Done!\n"




