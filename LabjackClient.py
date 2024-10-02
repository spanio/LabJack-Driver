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

    def configure_measurement_type(self, channel, measurement_type="single-ended", differential_negative_channel=None):
        """Configure the measurement type for a specific channel (single-ended or differential)."""
        if measurement_type == "single-ended":
            negative_channel_val = 199  # GND for single-ended
        elif measurement_type == "differential":
            if differential_negative_channel is None:
                raise ValueError("You must specify a valid negative channel for differential measurements.")
            negative_channel_val = differential_negative_channel
        else:
            raise ValueError("Invalid measurement type. Use 'single-ended' or 'differential'.")

        try:
            ljm.eWriteName(self.handle, f"AIN{channel}_NEGATIVE_CH", negative_channel_val)
            print(f"Configured AIN{channel} for {measurement_type} measurement with negative channel {negative_channel_val}")
        except ljm.LJMError as e:
            raise Exception(f"Failed to configure measurement type: {e}")

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


if __name__ == "__main__":
    try:
        # Create LabJack T7 driver instance using specific IP address
        labjack = LabJackT7Driver(ip_address="172.18.120.132")

        # Configure analog input ranges and negative channels for single-ended measurements
        labjack.set_range(0, "10V")
        labjack.configure_measurement_type(0, measurement_type="single-ended")

        # Configure differential measurement for AIN2 with AIN3 as the negative channel
        labjack.set_range(2, "10V")
        labjack.configure_measurement_type(2, measurement_type="differential", differential_negative_channel=3)

        # Read analog values from the first 4 channels
        analog_values = labjack.read_samples([f"AIN{i}" for i in range(4)])
        print("Analog Input Values:", analog_values)

    except Exception as e:
        print(f"Error: {e}")
