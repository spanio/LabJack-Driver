from labjack import ljm

class LabJackT7Driver:
    # Voltage range options for analog inputs
    voltage_ranges = {
        "10V": 10.0,
        "1V": 1.0,
        "0.1V": 0.1,
        "0.01V": 0.01
    }

    def __init__(self, ip_address="172.18.120.132", connection_type="ETHERNET", voltage_range="10V"):
        # Open the LabJack device over Ethernet with a specific IP address
        self.handle = ljm.openS("T7", connection_type, ip_address)
        self.device_info = ljm.getHandleInfo(self.handle)
        self.num_analog_inputs = 8  # Default for 8 analog inputs

        print(f"Opened LabJack T7: {self.device_info}")

    def set_range(self, channel, voltage_range):
        """Set the voltage range for a specific analog input channel."""
        if voltage_range not in self.voltage_ranges:
            raise ValueError(f"Invalid voltage range: {voltage_range}")

        try:
            ljm.eWriteName(self.handle, f"AIN{channel}_RANGE", self.voltage_ranges[voltage_range])
            print(f"Set AIN{channel} range to {voltage_range}")
        except ljm.LJMError as e:
            raise Exception(f"Failed to set voltage range: {e}")

    def configure_negative_channel(self, channel, negative_channel="GND"):
        """Configure the negative channel for differential readings (default to GND)."""
        if negative_channel == "GND":
            negative_channel_val = 199  # GND according to LabJack documentation
        else:
            try:
                negative_channel_val = int(negative_channel)
                if negative_channel_val < 0 or negative_channel_val >= self.num_analog_inputs:
                    raise ValueError("Invalid negative channel")
            except ValueError:
                raise Exception("Negative channel must be either 'GND' or a valid AIN channel number")

        try:
            ljm.eWriteName(self.handle, f"AIN{channel}_NEGATIVE_CH", negative_channel_val)
            print(f"Configured AIN{channel} negative channel to {negative_channel}")
        except ljm.LJMError as e:
            raise Exception(f"Failed to configure negative channel: {e}")

    def read_samples(self, channels=None):
        """Read analog input values from specified channels."""
        if channels is None:
            channels = [f"AIN{i}" for i in range(self.num_analog_inputs)]  # Default to reading all channels

        try:
            values = ljm.eReadNames(self.handle, len(channels), channels)
            print(f"Read analog values: {dict(zip(channels, values))}")
            return dict(zip(channels, values))
        except ljm.LJMError as e:
            raise Exception(f"Failed to read analog inputs: {e}")
        
    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        """Close the LabJack device connection."""
        ljm.close(self.handle)
        print("Closed LabJack connection.")


# Example usage of the LabJackT7Driver
if __name__ == "__main__":
    try:
        # Create LabJack T7 driver instance using specific IP address
        labjack = LabJackT7Driver(ip_address="172.18.120.132")

        # Configure analog input ranges and negative channels
        labjack.set_range(0, "10V")
        labjack.configure_negative_channel(0, "GND")

        # Read analog values from the first 4 channels
        analog_values = labjack.read_samples([f"AIN{i}" for i in range(4)])
        print("Analog Input Values:", analog_values)

        # Set digital output on FIO1 (as an example)
        labjack.write_digital_output(1, 1)

    except Exception as e:
        print(f"Error: {e}")


