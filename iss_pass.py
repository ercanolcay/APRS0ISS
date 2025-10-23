#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime, timezone
import pytz
import requests
import os

# --- CONFIGURATION ---
API_KEY = "" # "Your n2yo.com API Key"
NORAD_ID = 25544 # ISS NORAD ID
LATITUDE =  #Your QTH Latitude
LONGITUDE =  # Your QTH Longitude
ALTITUDE =  # Your QTH Altitude in Meters
DAYS = 2 # Check passes for the next N days
MIN_ELEVATION = 10 # Minimum elevation in degrees for a valid pass
TZ = pytz.timezone('Europe/Istanbul') # Your local timezone (Update if necessary)

# --- Log Function ---
LOG_FILE = "/home/pi/isstracker/iss-pass.log"
def log(msg):
    ts = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# --- Bash Script Files ---
BASH_NORMAL = "/home/pi/isstracker/direwolf-144800.sh"
BASH_ISS = "/home/pi/isstracker/direwolf-145825.sh"

# --- Direwolf + RTL_FM Control ---
def stop_direwolf():
    log("Stopping existing direwolf and rtl_fm processes...")
    os.system("pkill -f rtl_fm")
    os.system("pkill -f direwolf")

def start_direwolf(bash_file):
    log(f"Starting Direwolf with: {bash_file}")
    # The & runs the bash script in the background
    os.system(f"bash {bash_file} &")

# --- Fetch ISS Passes ---
def get_iss_passes():
    url = f"https://api.n2yo.com/rest/v1/satellite/radiopasses/{NORAD_ID}/{LATITUDE}/{LONGITUDE}/{ALTITUDE}/{DAYS}/{MIN_ELEVATION}/&apiKey={API_KEY}"
    for attempt in range(5):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            passes = resp.json().get("passes", [])
            for p in passes:
                # Convert UTC timestamps to local timezone aware datetime objects
                p["start_dt"] = datetime.fromtimestamp(p["startUTC"], timezone.utc).astimezone(TZ)
                p["end_dt"] = datetime.fromtimestamp(p["endUTC"], timezone.utc).astimezone(TZ)
            return passes
        except Exception as e:
            log(f"API request failed ({attempt+1}/5): {e}, retrying in 10 seconds.")
            time.sleep(10)
    return []

# --- Main Loop ---
def main_loop():
    # Start the iGate on the normal frequency first when the script begins
    start_direwolf(BASH_NORMAL)
    
    while True:
        passes = get_iss_passes()
        if not passes:
            log("No ISS pass information received. Waiting 10 minutes...")
            time.sleep(600) # Wait 10 minutes (600 seconds)
            continue

        for p in passes:
            start = p["start_dt"]
            end = p["end_dt"]
            now = datetime.now(TZ)

            # 1. Wait until the pass starts
            if now < start:
                wait_seconds = (start - now).total_seconds()
                log(f"🕒 Waiting {int(wait_seconds)} seconds until pass start.")
                time.sleep(wait_seconds)

            # --- 2. ISS PASS START ---
            log("🚀 ISS pass started. Switching to 145.825 MHz.")
            stop_direwolf()
            start_direwolf(BASH_ISS)

            # 3. Keep the ISS frequency running until the pass ends
            while datetime.now(TZ) < end:
                # Check frequently if the pass is over
                time.sleep(5) 

            # --- 4. ISS PASS END ---
            log("🔵 ISS pass finished. Returning to 144.800 MHz.")
            stop_direwolf()
            start_direwolf(BASH_NORMAL)

        log("🎯 All scheduled passes processed. Waiting 24 hours for new pass data...")
        time.sleep(48*3600) # Wait 48 hours before fetching new passes

if __name__ == "__main__":
    # Ensure the system reverts to 144.800 MHz if the script is stopped abruptly
    try:
        main_loop()
    finally:
        # Final cleanup and return to normal operation
        stop_direwolf()
        start_direwolf(BASH_NORMAL)