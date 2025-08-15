#!/bin/bash

# Updates the code for running the clock from github
# Your local configuration will probably conflict with the main one
# so this script temporarily copies it out and then restores it

printf "Updating the clock code from github\n\n"

cd /home/clock/wordclock

printf "Backing up local configuration ..."
cp config/config.sh config/config.bak
printf "Done!\n"

printf "Getting latest code from github ..."
git pull origin main
printf "Done!\n"

printf "Restoring local configuration ..."
cp config/config.bak config/config.sh
printf "Done!\n\n"

printf "Your system is now up to date!\n\n"

