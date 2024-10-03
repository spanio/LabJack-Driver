from LabjackClient import LabJackT7Driver

# LabJack IP Address
LABJACK_IP = "172.18.120.132"

# Initialize the LabJackT7Driver with the IP address, voltage range as a string, and enable RMS calculation
client = LabJackT7Driver(ip_address=LABJACK_IP, voltage_range="10V")

try:
    # Start the LabJack client (opens the connection and configures the voltage range for each channel)
    client.start()

    # Optionally, assign custom channel names
    client.set_channel_name(0, "Temperature_Sensor")
    client.set_channel_name(1, "Pressure_Sensor")
    client.set_channel_name(2, "Voltage_Sensor")
    client.set_channel_name(3, "Current_Sensor")

    # Display channel names for verification
    print("Configured Channel Names: ", client.get_channel_names())

    # Configure AIN0 for a differential measurement with AIN1 as the negative channel, and enable RMS calculation
    client.configure_measurement_type(0, measurement_type="differential", differential_negative_channel=1)
    client.set_channel_rms(0, True)  # Enable RMS for channel 0

    # Configure AIN2 for a single-ended measurement (referenced to GND), and disable RMS calculation
    client.configure_measurement_type(2, measurement_type="single-ended")
    client.set_channel_rms(2, False)  # Disable RMS for channel 2

    # Read analog input values from all channels and print the results
    analog_values = client.read_samples()
    print("Analog Input Values: ", analog_values)

except Exception as e:
    print(f"Error: {e}")

finally:
    # Ensure the client is closed properly
    client.close()
