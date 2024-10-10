from labjack import ljm
import logging

class LabJackT7Driver:
    voltage_ranges = {
        "10V": 10.0,
        "1V": 1.0,
        "0.1V": 0.1,
        "0.01V": 0.01,
        "-1V": 1.0  # Special case for -1V to 1V range
    }

    def __init__(self, ip_address="172.18.120.132", connection_type="ETHERNET", voltage_range="-1V"):
        self.handle = None
        self.num_analog_inputs = 16  # Default for 16 analog inputs
        self.channel_rms_flags = {}  # Store per-channel RMS flags
        self.channel_types = {}  # Store channel measurement types (single-ended or differential)
        self.voltage_range = voltage_range
        self.ip_address = ip_address
        self.connection_type = connection_type
        self.resolution_index = 0  # Auto-resolution by default

    def start(self):
        try:
            self.handle = ljm.openS("T7", self.connection_type, self.ip_address)
            self.device_info = ljm.getHandleInfo(self.handle)
            logging.info(f"Opened LabJack T7: {self.device_info}")
            
            for i in range(self.num_analog_inputs):
                self.set_range(i, self.voltage_range)
                self.set_resolution_index(i, 0)  # Auto-resolution index
        except ljm.LJMError as e:
            logging.error(f"Error opening LabJack T7: {e}")
            raise Exception(f"Failed to start LabJack: {e}")

    def stop(self):
        try:
            ljm.eStreamStop(self.handle)
            logging.info("Stream stopped.")
        except ljm.LJMError as e:
            logging.warning(f"Stream not running or error stopping: {e}")

    def close(self):
        if self.handle:
            ljm.close(self.handle)
            logging.info("Closed LabJack connection.")

    def set_range(self, channel, voltage_range):
        if voltage_range not in self.voltage_ranges:
            raise ValueError(f"Invalid voltage range: {voltage_range}")
        try:
            ljm.eWriteName(self.handle, f"AIN{channel}_RANGE", self.voltage_ranges[voltage_range])
            logging.info(f"Set AIN{channel} range to {voltage_range}")
        except ljm.LJMError as e:
            raise Exception(f"Failed to set voltage range for channel {channel}: {e}")

    def set_resolution_index(self, channel, resolution_index):
        try:
            ljm.eWriteName(self.handle, f"AIN{channel}_RESOLUTION_INDEX", resolution_index)
            logging.info(f"Set AIN{channel} resolution index to {resolution_index}")
        except ljm.LJMError as e:
            raise Exception(f"Failed to set resolution index for channel {channel}: {e}")

    def configure_measurement_type(self, channel, measurement_type="single-ended", differential_negative_channel=None):
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
            logging.info(f"Configured AIN{channel} for {measurement_type} measurement with negative channel {negative_channel_val}")
            self.channel_types[channel] = measurement_type  # Store the channel type
        except ljm.LJMError as e:
            raise Exception(f"Failed to configure measurement type for channel {channel}: {e}")

    def set_channel_rms(self, channel, rms_enabled, num_scans=200, scan_time_microseconds=10000):
        """
        Enable or disable FlexRMS for a channel by setting the AIN#_EF_INDEX to the FlexRMS feature (index 44).
        Also allows setting the number of scans and scan time for FlexRMS functionality.
        
        :param channel: Channel number
        :param rms_enabled: Whether to enable or disable RMS
        :param num_scans: Number of scans to use for FlexRMS (default 200)
        :param scan_time_microseconds: Total time in microseconds for the FlexRMS scan (default 10,000 µs = 10 ms)
        """
        if rms_enabled:
            try:
                # Reset any existing extended feature on this channel before enabling FlexRMS
                ljm.eWriteName(self.handle, f"AIN{channel}_EF_INDEX", 0)
                logging.info(f"Reset existing extended feature for AIN{channel}")
                
                # Enable FlexRMS mode for this channel (EF_INDEX 10)
                ljm.eWriteName(self.handle, f"AIN{channel}_EF_INDEX", 10)  # Set to FlexRMS (EF_INDEX 10)
                ljm.eWriteName(self.handle, f"AIN{channel}_EF_CONFIG_A", num_scans)  # Set number of scans
                ljm.eWriteName(self.handle, f"AIN{channel}_EF_CONFIG_B", scan_time_microseconds)  # Set scan time
                logging.info(f"Enabled FlexRMS for AIN{channel} with {num_scans} scans over {scan_time_microseconds} µs")
            except ljm.LJMError as e:
                raise Exception(f"Failed to enable FlexRMS for AIN{channel}: {e}")
        else:
            try:
                # Disable FlexRMS mode for this channel
                ljm.eWriteName(self.handle, f"AIN{channel}_EF_INDEX", 0)  # Disable extended feature
                logging.info(f"Disabled FlexRMS for AIN{channel}")
            except ljm.LJMError as e:
                raise Exception(f"Failed to disable FlexRMS for AIN{channel}: {e}")
        
        self.channel_rms_flags[channel] = rms_enabled

    def read_samples(self):
        """
        Read samples from the LabJack device. Uses built-in FlexRMS if enabled.
        Ensures that FlexRMS values are always non-negative.
        Handles LJMError 2588 (AIN_EF_COULD_NOT_FIND_PERIOD) by returning a default value (e.g., 0) if no period is found.
        """
        results = {}

        for channel in range(self.num_analog_inputs):
            try:
                if self.channel_rms_flags.get(channel, False):
                    # Try to read FlexRMS value from the AIN#_EF_READ_A register
                    try:
                        value = ljm.eReadName(self.handle, f"AIN{channel}_EF_READ_A")
                        logging.info(f"Read FlexRMS value for AIN{channel}: {value}")
                        value = abs(value)  # Ensure the FlexRMS value is non-negative
                    except ljm.LJMError as e:
                        if e.error == 2588:  # Handle AIN_EF_COULD_NOT_FIND_PERIOD
                            logging.warning(f"Could not find valid FlexRMS period for AIN{channel}. Returning 0.")
                            value = 0  # Return 0 or a default value
                        else:
                            raise e  # Re-raise other errors
                else:
                    # Read normal voltage value
                    value = ljm.eReadName(self.handle, f"AIN{channel}")
                    logging.info(f"Read value for AIN{channel}: {value}")
                results[f"AIN{channel}"] = value
            except ljm.LJMError as e:
                raise Exception(f"Failed to read samples for AIN{channel}: {e}")
        
        return results
