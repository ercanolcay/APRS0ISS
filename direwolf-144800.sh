#!/bin/bash

# Stop any running rtl_fm and direwolf processes (if they exist)
# Prevents conflicts when switching frequencies.
pgrep rtl_fm && pkill -f rtl_fm
pgrep direwolf && pkill -f direwolf

# Short pause to ensure processes are completely terminated
sleep 1

# Start RTL_FM on 144.800 MHz and pipe audio output to Direwolf
# Configuration file: sdr.conf (for standard terrestrial APRS)
/usr/local/bin/rtl_fm -M fm -f 144.800M - | /usr/local/bin/direwolf -c /home/pi/isstracker/sdr.conf -r 24000 -D 1 -