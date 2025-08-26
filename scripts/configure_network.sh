#!/bin/bash

# This script is used to configure the network connection to the Wifi

# Default settings
SSID="None"
SECURITY="WEP"
PASSWORD="Password"
HIDDEN=0
SET_IP=0
IP=""
WAITTIME=10

printf "\n"

# Checking for command line parameters
VALID_ARGS=$(getopt -o h --long help,ssid:,security:,password:,hidden,ip:,wait: -- "$@")
if [[ $? -ne 0 ]]; then
  exit 1;
fi

eval set -- "$VALID_ARGS"

while [ : ];do
  case "$1" in
    -h | --help)
      printf "Usage: configure_network.sh --help --ssid <SSID> --security <WEP|WPA|WPA2,nopass> --password <PASSWORD> --IP <FIXED IP ADDRESS> --WAIT <time(s) to wait for WIFI) --hidden\n"
      exit 0
      shift
      ;;
    --ssid)
      SSID="$2"
      shift 2
      ;;
    --security)
      SECURITY="$2"
      shift 2
      ;;
    --password)
      PASSWORD="$2"
      shift 2
      ;;
    --ip)
      SET_IP=1
      IP="$2"
      shift 2
      ;;
    --hidden)
      HIDDEN=1
      shift
      ;;
    --wait)
      WAITTIME=$(($2 * 1))
      shift 2
      ;;
    --)
      shift;
      break
      ;;
  esac
done

# Confirm the settings

printf "Creating network\n"
printf " - SSID $SSID\n"
printf " - Security $SECURITY\n"
printf " - Password $PASSWORD\n"
if [ $HIDDEN -eq 1 ]; then
  printf " - Hidden\n"
else
  printf " - Not hidden\n"
fi
if [ $SET_IP -eq 0 ]; then
  printf " - Dynamic IP address\n"
else
  printf " - Fixed IP $IP\n"
fi

printf "\n"

# Name the file

FILENAME="/etc/NetworkManager/system-connections/$SSID.nmconnection"

# Get linux timestamp

TIMESTAMP=`date +%s`

# Get a UUID to use for the connection

UUID=`uuidgen --time`

# Write the settings to a file

cat > $FILENAME << EOF
[connection]
id=$SSID
uuid=$UUID
type=wifi
interface-name=wlan0
timestamp=$TIMESTAMP

[wifi]
mode=infrastructure
ssid=$SSID

[wifi-security]
key-mgmt=$SECURITY-psk
psk=$PASSWORD

EOF

if [ $SET_IP -ne 0 ]; then
cat >> $FILENAME << EOF

[ipv4]
address1=$IP/24,192.168.1.1
dns=8.8.8.8;8.8.4.4;
method=auto

EOF
fi

# Set the correct file permissions or NetworkManager will not load the file

chmod 600 $FILENAME

printf "Written Network Manager file\n"

# Restart the Network Manager service

printf "Restarting the Network Manager service ..."
systemctl restart NetworkManager
printf "Done!\n"

# Wait until the network connects

printf "Waiting for WiFi to connect ..."
counter=$WAITTIME

while [ $counter -gt 0 ]
do
  RESULT=`nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d\' -f2`
  if [[ $RESULT == "yes:$SSID" ]]; then
    printf "Done!\n"
    exit 0
  fi
  printf "$counter."
  ((counter=$counter-1))
  sleep 1
done

printf " Timed Out!\n"
printf "\nNetwork did not connect in time\n"
exit 2



