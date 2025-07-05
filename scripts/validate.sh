#!/bin/bash

# Script to validate the configuration of the RPI
# to see if everything should be working.

R="\033[31m"
G="\033[32m"
Y="\033[33m"
W="\033[0m"
B="\e[1;36m"

printf "\nChecking overall configuration for errors.\n\n"

# Overall info
DEVICE=`ip -br link show | awk 'NR==2{print $1}'`
IP=`ip -4 a show $DEVICE | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`
HOSTNAME=`hostname`

printf "$G - This machine is: $B $HOSTNAME - $IP ($DEVICE)\n"
printf "$W"

# SPIDEV enabled
SPI=`sudo raspi-config nonint get_spi`
if [ $SPI -eq 0 ]; then
  printf "$G - SPI looks to be enabled\n"
else
  printf "$R - SPI doesn't seem to be enabled - clock will not be able to control lights\n"
fi

printf "$W"

# HWC enabled
dmesg | grep -q  "rtc-ds1307"
if [ "$?" -eq 0 ]; then
  printf "$G - RTC looks to be enabled\n"
else
  # No RTC - but maybe we have NTP service
  sudo timedatectl | grep -q "NTP service: active"
  if [ "$?" -eq 0 ]; then
    printf "$Y - No RTC but NTP is active so clock will be OK as long as it has WIFI connection\n"
  else
    printf "$R - RTC doesn't seem to be enabled or did not start and NTP is not set - clock will be wrong after a power cut\n"
  fi
fi

printf "$W"


# Boot behaviour
BOOT=`sudo raspi-config nonint get_autologin`
if [ $BOOT -eq 1 ]; then
  printf "$G - Booting into the command line\n"
else
  printf "$R - Not booting into the command line - may cause issues or slowness\n"
fi

printf "$W"

# Services
CLOCK=`systemctl is-active  clock-startup-script.service`
if [ "$CLOCK" == "active" ]; then
  printf "$G - Clock main service is active\n"
else
  printf "$R - Clock service 'clock-startup-script.service' is not active - clock will not be running\n"
fi

UI=`systemctl is-active  clock-ui-script.service`
if [ "$UI" == "active" ]; then
  printf "$G - Clock UI front end service is active at $B http://$IP:8000/config\n"
else
  printf "$R - Clock UI front end service 'clock-ui-script.service' is not active - will not be able to use web front end\n"
fi


printf "$W"

printf "\nChecks completed\n\n"
