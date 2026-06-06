import time
import numpy as np
import json 
import os 

# Import your settings
from data_collector import get_rssi_from_os, SAMPLE_RATE 
WINDOW_SIZE = 10

def predict_crowd_level(rssi_values):
    avg = sum(rssi_values) / len(rssi_values)

    if avg >= -55:
        return "LOW"
    elif avg >= -65:
        return "MEDIUM"
    else:
        return "HIGH"

OUTPUT_FILE = "level.txt" 
TEMP_FILE = "level.tmp"

print("--- DEBUG MODE STARTED ---")
print(f"I will attempt to create '{OUTPUT_FILE}' in this folder.")
print("Press Ctrl+C to stop.")

live_rssi_window = []
current_prediction = "WAITING..." 

try:
    while True:
        # 1. Get RSSI
        rssi_value = get_rssi_from_os()
        
        if rssi_value is not None:
            # 2. Add to window
            live_rssi_window.append(rssi_value)
            print(f"Got RSSI: {rssi_value} dBm... ({len(live_rssi_window)}/{WINDOW_SIZE})")

            # 3. Update Prediction if window is full
            if len(live_rssi_window) == WINDOW_SIZE:
                data_for_model = np.array(live_rssi_window)
                current_prediction = predict_crowd_level(data_for_model)
                live_rssi_window.pop(0) 

            # 4. WRITE TO FILE (The part that was failing)
            output_data = {
                "level": current_prediction,
                "rssi": int(rssi_value)
            }
            
            try:
                # Write to a temp file first
                with open(TEMP_FILE, 'w') as f:
                    json.dump(output_data, f)
                    f.flush() # Force write to disk
                    os.fsync(f.fileno()) # Double force write

                # Rename temp file to real file
                os.replace(TEMP_FILE, OUTPUT_FILE)
                
                # *** DEBUG MESSAGE ***
                print(f" -> SUCCESS: Updated level.txt with {rssi_value} dBm")
                
            except Exception as e:
                print(f" -> WRITE ERROR: {e}")

        else:
            print("No signal found...")
            
        time.sleep(0.5) 

except KeyboardInterrupt:
    print("\nStopped.")
except Exception as e:
    print(f"Critical Error: {e}")