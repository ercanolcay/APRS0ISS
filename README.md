# APRS0ISS: Automatic ISS Frequency Switching iGate (RTL-SDR / Pi Zero 2 W)

**APRS0ISS** provides an automated solution for RTL-SDR based APRS iGates to intelligently switch from the standard terrestrial frequency (144.800 MHz) to the International Space Station's (ISS) APRS frequency (145.825 MHz) during an overhead pass, and then automatically revert to normal operations.

The core of the project is a Python script that uses the **n2yo.com API** to predict ISS passes and manages the `direwolf` and `rtl_fm` processes accordingly.

## 🚀 Key Features

* **Automatic Frequency Management:** Hops to 145.825 MHz when the ISS is visible, and returns to 144.800 MHz when the pass is complete.
* **Low-Power Operation:** Designed for the Raspberry Pi Zero 2 W, utilizing minimal resources for 24/7 operation.
* **Log Management:** All operations and pass predictions are logged to a dedicated file (`iss-pass.log`).
* **Reliable Pass Prediction:** Uses the n2yo.com API for accurate pass timing.

## ⚙️ Requirements

### Hardware
* Raspberry Pi Zero 2 W (or similar Pi model)
* RTL-SDR 
* Appropriate Antenna for 144-146 MHz

### Software Dependencies

The following packages and libraries must be installed on your Raspberry Pi:

| Package Type | Dependency | Purpose |
| :--- | :--- | :--- |
| **Linux Tools** | `direwolf` | APRS TNC emulator. |
| **Linux Tools** | `rtl-sdr` | Tools for the RTL-SDR dongle (specifically `rtl_fm`). |
| **Python** | `python3`, `python3-pip` | Required for the main control script. |
| **Python Library** | `requests` | To communicate with the n2yo.com API. |
| **Python Library** | `pytz` | For handling local timezone conversions. |

**Installation Commands:**

```bash
# Update and install core Linux packages
sudo apt update
sudo apt install direwolf rtl-sdr git python3 python3-pip

## Install required Python libraries
pip3 install requests pytz
```

## 🛠️ Setup and Configuration
1. Project Files
Clone the repository and move into the directory:
```
git clone [https://github.com/ercanolcay/APRS0ISS.git](https://github.com/ercanolcay/APRS0ISS.git)
cd APRS0ISS
```
Place all script files (iss_pass.py, direwolf-144800.sh, direwolf-145825.sh) and your two direwolf configuration files (sdr.conf and sdr_iss.conf) into the /home/pi/isstracker/ directory, as referenced in the scripts.

2. Configure iss_pass.py
Edit the main control script (iss_pass.py) and update the CONFIGURATION section with your QTH and API details:
```
# --- CONFIGURATION ---
API_KEY = "YOUR_N2YO_API_KEY"  # <-- IMPORTANT: Get your key from n2yo.com
NORAD_ID = 25544             # ISS NORAD ID (Default)
LATITUDE =                   # Your QTH Latitude
LONGITUDE =                  # Your QTH Longitude
ALTITUDE =                   # Your QTH Altitude in meters
TZ = pytz.timezone('Europe/Istanbul') # Your local timezone
# ... other settings
```
3. Configure Bash Scripts
Ensure the two bash scripts are executable and note that the ISS script requires `sudo`:
```
chmod +x /home/pi/isstracker/*.sh
```
Configuration Note: Ensure your `sdr_iss.conf` file is specifically optimized for $145.825 \text{ MHz}$ APRS packets from space (e.g., proper AFSK level).4. Automated Startup (Crontab)To ensure the frequency management script starts automatically after every reboot, add the following entry to your crontab:
```
crontab -e
```
Add this line to the end of the file, save, and exit:
```
@reboot /usr/bin/python3 /home/pi/isstracker/iss_pass.py >> /home/pi/isstracker/iss-pass.log 2>&1 &
```
This command runs the Python script in the background (&) and redirects all output to the log file.
| File Name | Language | Description |
| :--- | :--- | :--- |
| `iss_pass.py` | Python 3 | The core scheduler. Manages the n2yo.com API calls, calculates wait times, and controls which bash script is running (144.800 MHz or 145.825 MHz). |
| `direwolf-144800.sh` | Bash | Starts `rtl_fm` on 144.800 MHz and pipes the output to `direwolf` for standard terrestrial iGate operation. |
| `direwolf-145825.sh` | Bash | Stops normal operation and starts `rtl_fm` (with sudo) on 145.825 MHz, piping to `direwolf` with the dedicated ISS configuration file. |
