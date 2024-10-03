import yaml
from LabjackClient import LabJackT7Driver

# Load the YAML configuration file
with open('config.yaml', 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

# Extract LabJack configuration
labjack_config = config['hardware'][0]  # Assuming LabJack is the first device in the hardware section

# Initialize the LabJack driver with the IP and voltage range
client = LabJackT7Driver(ip_address=labjack_config['IP'], voltage_range=labjack_config['Voltage_range'])

# Start the LabJack device
client.start()

# Configure each channel as per the YAML configuration
for channel_name, channel_config in labjack_config['Channels'].items():
    channel_num = int(channel_name.split()[-1])  # Extract channel number
    
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

# Read and print the samples
analog_values = client.read_samples()
print("Analog Input Values: ", analog_values)

# Close the connection
client.close()
