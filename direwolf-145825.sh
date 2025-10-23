#!/bin/bash

# Stop any running rtl_fm and direwolf processes (if they exist)
pgrep rtl_fm && pkill -f rtl_fm
pgrep direwolf && pkill -f direwolf

# Short pause to ensure processes are completely terminated
sleep 1

# Start RTL_FM on ISS frequency (145.825 MHz) and pipe the audio output to Direwolf.
# NOTE: 'sudo' is used here for rtl_fm to ensure correct execution.
# Configuration file: sdr_iss.conf (dedicated for ISS decoding)
sudo /usr/local/bin/rtl_fm -M fm -f 145.825M - | /usr/local/bin/direwolf -c /home/pi/isstracker/sdr_iss.conf -r 24000 -D 1 -