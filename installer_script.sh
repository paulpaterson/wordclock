#!/bin/bash

# This script is used to configure the Raspberry PI machine to be able to run the software
# Run it *once* before running the software

#set -e

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
printf "Fixing SPI buffer size ..."
sudo cp spidev.conf /etc/modprobe.d/spidev.conf
printf "Done!\n"

# Enabling the real time clock

printf "Enabling Real Time Clock module ... "
# Check location of config 
if [ -d "/etc/boot/firmware" ]; then
  config_file="/boot/firmware/config.txt"
else
  config_file="/boot/config.txt"
fi
sudo sed -i "1i# Real Time Clock\ndtoverlay=i2c-rtc,ds3231" $config_file
printf "Done!\n"
printf "Setting the time for the Real Time Clock ... "
sudo hwclock -w
printf "Done!\n"



# UV - needed to run Python

if [ -f "/home/clock/.local/bin/uv" ]; then
    printf "UV already found - skipping installation\n"
else
    printf "Installing UV to run the Python code ... this may take a while:\n"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    printf "Done!\n"
    printf "Copying UV so it can be used globally ... "
    sudo ln -s /home/clock/.local/bin/uv /bin/uv
    printf "Done!\n"
fi


# Get the right version of Python on the machine

printf "Installing the required python version ... takes a while\n"
uv python install 3.11
printf "\nDone!\n"

# Sync the environment for UV

printf "Syncing UV environment ... this may take a while:\b"
uv sync
printf "Done!\n"

# SystemD services to run the clock
printf "Copying the systemd services ... "
sudo ln -s /home/clock/wordclock/clock-startup-script.service /etc/systemd/system/clock-startup-script.service
sudo ln -s /home/clock/wordclock/clock-ui-script.service /etc/systemd/system/clock-ui-script.service
printf "Done!\n"
printf "Enabling the systemd services ... "
sudo systemctl enable clock-startup-script.service
sudo systemctl enable clock-ui-script.service
printf "Done!\n"


