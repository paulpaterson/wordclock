#!/bin/bash

# This script is used to configure the Raspberry PI machine to be able to run the software
# Run it once before running the software. It is safe to run it multiple times in you want to 
# change the options

#set -e


# Default settings
TEST=0
FISH=0
SSH=0
RTC=0
RESTORE=0
SET_NAME=0
HOSTNAME=""
EXISTING_HOSTNAME=`hostname`
DEVICE=`ip -br link show | awk 'NR==2{print $1}'`
IP=`ip -4 a show $DEVICE | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`

cd /home/clock/wordclock || exit


# Checking for command line parameters
VALID_ARGS=$(getopt -o th  --long test,fish,ssh,rtc,restore,help,name: -- "$@")
if [[ $? -ne 0 ]]; then
  exit 1;
fi

eval set -- "$VALID_ARGS"

while [ : ];do
  case "$1" in
    -h | --help)
	   printf "Usage: ./scripts/installer_script.sh --test --fish --ssh --rtc --restore\n"
	   exit 0
	   shift
	   ;;
    -t | --test)
           TEST=1
	   shift
           ;;
    --fish)
	   FISH=1
	   shift
	   ;;
    --ssh)
	   SSH=1
	   shift
	   ;;
    --rtc)
	   RTC=1
	   shift
           ;;
    --restore)
           RESTORE=1
	   shift
           ;;
    --name)
	   SET_NAME=1
	   HOSTNAME="$2"
	   shift 2
	   ;;
    --)	   shift;
	   break
	   ;;
  esac
done

if [ $TEST -eq 1 ]; then
  printf "Configuring as a test machine\n\n"
else
  printf "Configuring as a full hardware implementation\n\n"
fi

# Setting the machine name
if [ $SET_NAME -eq 1 ]; then
  printf "Changing the hostname from $EXISTING_HOSTNAME to $HOSTNAME ... "
  sudo hostnamectl set-hostname $HOSTNAME
  sudo sed -i "s/$EXISTING_HOSTNAME/$HOSTNAME/g" /etc/hosts
  printf "Done!\n"
else
  printf "Not setting the hostname of this machine - kept as '$EXISTING_HOSTNAME'\n"
fi

# Check location of config
if [ -d "/boot/firmware" ]; then
  config_file="/boot/firmware/config.txt"
else
  config_file="/boot/config.txt"
fi

# Create backup files if they don't exist

if [ -f "backups/config.txt" ]; then
  if [ $RESTORE -eq 1 ]; then
    printf "Restoring backups files ... "
    sudo cp "backups/config.txt" "$config_file"
    sudo cp "backups/hosts" "/etc/hosts"
    sudo cp "backups/shells" "/etc/shells" 
    printf "Done!\n"
    exit 0
  else
    printf "Backup files already exist.\n"
  fi
else
  if [ $RESTORE -eq 1 ]; then
    printf "Cannot restore from backup - backup files are not in backups folder\n"
    exit 1
  fi
  printf "Backing up config files ... "
  sudo cp "$config_file" "backups/config.txt"
  sudo cp "/etc/hosts" "backups/hosts"
  sudo cp "/etc/shells" "backups/shells"
  printf "Done!\n"
fi


# BOOT Behaviour

printf "Setting machine to boot to command line ... "
sudo raspi-config nonint do_boot_behaviour B1
printf "Done!\n"

# SSH logging in - disable if you don't want this

if [ $SSH -eq 1 ]; then
  printf "Turning on SSH ... "
  sudo raspi-config nonint do_ssh 0
  printf "Done!\n"
  printf "You can ssh into this machine now at address: "
  printf "$IP ($DEVICE)\n"
else
  printf "Skipping SSH configuration\n"
fi

# SPI Interface - needed for the matrix control

if [ $TEST -eq 0 ]; then
  printf "Turning on the SPI interface ..."
  sudo raspi-config nonint do_spi 0
  printf "Done!\n"
else
  printf "Test hardware - Skipping turning on SPI interface\n"
fi

printf "Fixing SPI buffer size ..."
sudo cp config/spidev.conf /etc/modprobe.d/spidev.conf
printf "Done!\n"

# Enabling the real time clock

if [ $RTC -eq 1 ]; then
  printf "Enabling Real Time Clock module ... "
  if grep -q "dtoverlay=i2c-rtc,ds3231" "$config_file"; then 
    printf "Already set!\n" 
  else 
    sudo sed -i "1i# Real Time Clock\ndtoverlay=i2c-rtc,ds3231" $config_file
    printf "Done!\n"
  fi
else
  printf "Skipping RTC installation\n"
fi


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
  sudo rm /etc/systemd/system/clock-startup-script.service
fi
sudo ln -s /home/clock/wordclock/services/clock-startup-script.service /etc/systemd/system/clock-startup-script.service
printf "Done!\n"

printf "Copying the systemd UI service ... "
if [ -f "/etc/systemd/system/clock-ui-script.service" ]; then
  sudo rm /etc/systemd/system/clock-ui-script.service
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
  printf "# Actual hardware settings\nexport CLOCK_BUTTON_PIN=27\nexport CLOCK_MODE_BUTTON_PIN=25\n" > config/local_config.sh
  printf "Done!\n"
else
 printf "Creating local config as simulated clock ... "
 printf "# Simulated hardware - no settings\n" > config/local_config.sh
 printf "Done!\n"
fi

# FISH shell installation - optional
if [ $FISH -eq 1 ]; then
  printf "Installing FISH shell as default ... make take a while\n"
  sudo apt -y install fish
  sudo sh -c 'echo $(which fish) >> /etc/shells'
  sudo chsh -s "$(which fish)" clock
fi
