#!/bin/bash

# This script is used to configure the Raspberry PI machine to be able to run the software
# Run it *once* before running the software

#set -e

# Check installation type
#   - default = hardware machine
#   - test    = test or virtual machine, which does not have all the relevant hardware attached
#   - fish    = also install the FISH shell and set it as default
#
# installer_script      -> default
# installer_script test|fish 

# Default settings
TEST=0
FISH=0

# Checking for command line parameters

for arg in "$@"; do
    case $arg in
       "test")
           TEST=1
           ;;
       "fish")
	   FISH=1
	   ;;
       *)
	   printf "Unknown command line parameter: $arg\n"
    esac
done

if [ $TEST -eq 1 ]; then
  printf "Configuring as a test machine\n"
else
  printf "Configuring as a full hardware implementation\n"
fi


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

if [ $TEST -eq 0 ]; then
  printf "Turning on the SPI interface ..."
  sudo raspi-config nonint do_spi 0
  printf "Done!\n"
else
  printf "Test hardware - Skipping turning on SPI interface\n"
fi

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
if [ $TEST -eq 0 ]; then
  printf "Installing hardware specific python packages ... "
  uv sync --group hardware
  printf "Done!\n"
else
  printf "Test hardware - Skipping hardware specific python packages\n"
fi

# SystemD services to run the clock

printf "Copying the systemd clock service ... "
if [ -f "/etc/systemd/system/clock-startup-script.service" ]; then
  sudo rm "/etc/systemd/system/clock-startup-script.service"
fi
sudo ln -s /home/clock/wordclock/services/clock-startup-script.service /etc/systemd/system/clock-startup-script.service
printf "Done!\n"

printf "Copying the systemd UI service ... "
if [ -f "/etc/systemd/system/clock-ui-script.service" ]; then
  sudo rm "/etc/systemd/system/clock-ui-script.service"
fi
sudo ln -s /home/clock/wordclock/services/clock-ui-script.service /etc/systemd/system/clock-ui-script.service
printf "Done!\n"

printf "Enabling the systemd services ... "
sudo systemctl daemon-reload
sudo systemctl enable clock-startup-script.service
sudo systemctl enable clock-ui-script.service
printf "Done!\n"

# Local configuration

if [ $TEST -eq 0 ]; then
  printf "Creating local config as hardware clock ... "
  printf "# Actual hardware settings\nexport CLOCK_BUTTON_PIN=27\nexport CLOCK_MODE_BUTTON_PIN=25\n" > local_config.sh
  printf "Done!\n"
else
 printf "Creating local config as simulated clock ... "
 printf "# Simulated hardware - no settings\n" > local_config.sh
 printf "Done!\n"
fi

# FISH shell installation - optional
if [ $FISH -eq 1 ]; then
  printf "Installing FISH shell as default ... make take a while\n"
  sudo apt -y install fish
  sudo sh -c 'echo $(which fish) >> /etc/shells'
  sudo chsh -s "$(which fish)" clock
fi
