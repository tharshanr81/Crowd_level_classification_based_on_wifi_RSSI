import subprocess
import time
import csv
import platform
import re
# --- IMPORTANT: CONFIGURATION ---
# Replace with the BSSID (MAC Address) of your target Access Point
TARGET_BSSID = "82:b7:74:a9:3d:4a" 
# How often to sample (in seconds)
SAMPLE_RATE = 0.5 
# The file to save data to
OUTPUT_FILE = "raw_rssi_data.csv" 
# --- END CONFIGURATION ---
def get_rssi_from_os():
    """
    This is the OS-specific function. It must be modified for your system.
    It should return a single integer (the RSSI value) or None if it fails.
    """
    os_name = platform.system()
    
    try:
        if os_name == "Windows":
            # --- Windows Command ---
            # This is complex because netsh returns a full report.
            # We look for the line with the BSSID and then the signal %
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"], 
                shell=True
            ).decode("utf-8")
            
            # Find the signal strength line for our target BSSID
            # This regex is an example; you may need to adjust it
            match = re.search(f"{TARGET_BSSID}[\s\S]*?Signal\s*:\s*(\d+)%", output)
            if match:
                signal_percent = int(match.group(1))
                # Convert percent to dBm (a rough, common approximation)
                # 0% = -100dBm, 100% = -50dBm
                rssi = (signal_percent / 2) - 100 
                return int(rssi)

        elif os_name == "Linux":
            # --- Linux Command ---
            # Make sure 'iw' and 'grep' are installed.
            # Replace 'wlan0' with your actual wireless interface
            interface = "wlan0"
            output = subprocess.check_output(
                f"iw dev {interface} link | grep -i 'signal' | grep -o '-\d*'",
                shell=True
            ).decode("utf-8")
            
            # The output should be just the number, e.g., "-58"
            return int(output.strip())

        elif os_name == "Darwin": # macOS
             # --- macOS Command ---
             # This is a common way; requires 'airport' utility
             # You may need to find the airport utility path
             path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
             output = subprocess.check_output([path, "-I"]).decode("utf-8")
             match = re.search(r"\s+agrCtlRSSI:\s+(-\d+)", output)
             if match:
                 return int(match.group(1))

    except Exception as e:
        print(f"Error getting RSSI: {e}")
        return None

    # Fallback or if OS not supported
    return None # Failed to get RSSI


print(f"Starting data collection... saving to {OUTPUT_FILE}")
print("Press Ctrl+C to stop.")

# Create the CSV file and write the header
try:
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "rssi"])

    # Main loop
    while True:
        rssi_value = get_rssi_from_os()
        
        if rssi_value is not None:
            current_time = time.time()
            print(f"Time: {current_time}, RSSI: {rssi_value} dBm")
            
            # Append the new data to the CSV
            with open(OUTPUT_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([current_time, rssi_value])
        else:
            print("Failed to get RSSI... retrying.")
            
        time.sleep(SAMPLE_RATE)

except KeyboardInterrupt:
    print("\nData collection stopped. File saved.")