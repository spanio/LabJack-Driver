from LabjackClient import LabJackT7Driver

# LabJack IP Address
LABJACK_IP = "172.18.120.132"

# Initialize the LabJackT7Driver with the IP address and voltage range as a string
client = LabJackT7Driver(ip_address=LABJACK_IP, voltage_range="10V")

try:
    # Configure the voltage range for AIN0 to ±10V and set the negative channel to GND
    client.set_range(0, "10V")
    client.configure_negative_channel(0, "GND")

    # Read analog input values from the first 4 channels
    analog_values = client.read_samples([f"AIN{i}" for i in range(4)])
    print(analog_values)

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
