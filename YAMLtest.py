import yaml
import time
import pandas as pd
from LabjackClient import LabJackT7Driver
import datetime
import sys
import os

# Function to clear the console screen
def clear_screen():
    if os.name == 'nt':
        os.system('cls')  # For Windows
    else:
        os.system('clear')  # For macOS/Linux

# Load the YAML configuration file
with open('config.yaml', 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

# Extract LabJack configuration
labjack_config = config['hardware'][0]  # Assuming LabJack is the first device in the hardware section

# Initialize the LabJack driver with the IP and voltage range
client = LabJackT7Driver(ip_address=labjack_config['IP'], voltage_range=labjack_config['Voltage_range'])

# Start the LabJack device
client.start()

# Create a dictionary to map channels from the YAML file
yaml_channels = {}
for channel_name, channel_config in labjack_config['Channels'].items():
    channel_num = int(channel_name.split()[-1])  # Extract channel number
    yaml_channels[channel_num] = channel_config['name']  # Store the channel name

    # Access properties directly by their keys in the channel configuration
    channel_type = channel_config['type']  # Extract channel type (single-ended or differential)
    rms_flag = channel_config['RMS']  # Check if RMS is enabled for this channel

    if channel_type == 'differential':
        negative_channel = channel_config['negative_channel']  # Extract negative channel for differential
        client.configure_measurement_type(channel_num, measurement_type="differential", differential_negative_channel=negative_channel)
    else:
        client.configure_measurement_type(channel_num, measurement_type="single-ended")

    # Set RMS flag for this channel
    client.set_channel_rms(channel_num, rms_flag)

# Define the sampling interval (e.g., 1 second for a 1Hz sample rate)
sampling_frequency_str = config.get('sampling_frequency', '1Hz')  # Default to 1Hz if not specified
sampling_interval = 1 / float(sampling_frequency_str[:-2])  # Convert '5Hz' to 5.0 and then to 0.2 seconds

# Initialize variables for counting and tracking time
count = 0
time_start = datetime.datetime.now(datetime.timezone.utc)

# Continuous data acquisition loop
try:
    print("Starting data acquisition... Press Ctrl+C to stop.")
    while True:
        # Read the samples from LabJack
        analog_values = client.read_samples()

        # Prepare the row dict with timestamp and values, only for channels listed in YAML
        row_dict = {'Timestamp': int(time.time()), 'time': pd.Timestamp.now()}
        for channel_num, channel_name in yaml_channels.items():
            if f"AIN{channel_num}" in analog_values:
                row_dict[channel_name] = analog_values[f"AIN{channel_num}"]

        # Calculate elapsed time
        time_now = datetime.datetime.now(datetime.timezone.utc)
        elapsed_time = time_now - time_start
        formatted_elapsed_time = str(elapsed_time).split('.')[0]  # Format the elapsed time

        # Clear the screen and print formatted output
        clear_screen()
        print("To stop data acquisition, type: CTRL+C\n")
        print(f"count: \t{count}\tTime Started: \t{time_start.isoformat()}\tElapsed Time: \t{formatted_elapsed_time}\n")
        print("Channel Data: ")

        ModuloCounter = 0  # Initialize a counter for formatting output
        for channel_name, value in row_dict.items():
            if channel_name not in ['count', 'Timestamp', 'time']:  # Skip 'count', 'Timestamp', and 'time'
                print(f"{channel_name}:\t{value}\t", end="")
                ModuloCounter += 1
                if ModuloCounter % 4 == 0:  # Print a newline after every 4th item
                    print("\n", end="")

        print("\n")  # Ensure a newline after all channel data has been printed

        # Increment the count for each loop
        count += 1

        # Wait for the next sample based on the sampling interval
        time.sleep(sampling_interval)
except KeyboardInterrupt:
    print("Data acquisition stopped.")
finally:
    # Close the connection
    client.close()
