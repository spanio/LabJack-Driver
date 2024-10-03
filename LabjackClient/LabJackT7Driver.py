from labjack import ljm
import math
import logging

class LabJackT7Driver:
    # Voltage range options for analog inputs
    voltage_ranges = {
        "10V": 10.0,
        "1V": 1.0,
        "0.1V": 0.1,
        "0.01V": 0.01
    }

    def __init__(self, ip_address="172.18.120.132", connection_type="ETHERNET", voltage_range="10V"):
        self.handle = None
        self.num_analog_inputs = 16  # Default for 8 analog inputs
        self.channel_names = [f"AIN{i}" for i in range(self.num_analog_inputs)]  # Default channel names
        self.channel_rms_flags = {}  # Store per-channel RMS flags
        self.channel_types = {}  # Store channel measurement types (single-ended or differential)
        self.voltage_range = voltage_range
        self.ip_address = ip_address
        self.connection_type = connection_type

    def start(self):
        try:
            # Open the LabJack device over Ethernet with a specific IP address
            self.handle = ljm.openS("T7", self.connection_type, self.ip_address)
            self.device_info = ljm.getHandleInfo(self.handle)
            logging.info(f"Opened LabJack T7: {self.device_info}")
            
            # Set the voltage range for each channel
            for i in range(self.num_analog_inputs):
                self.set_range(i, self.voltage_range)
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

    def set_channel_name(self, position, name):
        if position < 0 or position >= self.num_analog_inputs:
            raise ValueError(f"Invalid position value. Must be between 0 and {self.num_analog_inputs - 1}.")
        self.channel_names[position] = name

    def get_channel_names(self):
        return self.channel_names

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

    def set_channel_rms(self, channel, rms_enabled):
        self.channel_rms_flags[channel] = rms_enabled

    def read_samples(self):
        channels = [f"AIN{i}" for i in range(self.num_analog_inputs)]
        results = {}
        
        for channel in channels:
            try:
                if self.channel_rms_flags.get(channel, False):
                    # Calculate RMS for this channel
                    results[channel] = self._stream_rms_sequential([channel])
                else:
                    # Read normal samples
                    value = ljm.eReadName(self.handle, channel)
                    results[channel] = value
                    logging.info(f"Read value for {channel}: {value}")
            except ljm.LJMError as e:
                raise Exception(f"Failed to read samples for {channel}: {e}")
                
        return results

    def _stream_rms_sequential(self, channels):
        # Stream 1000 samples at 25000 samples per second per channel, sequentially.
        # This should give 3 full cycles of data at 60Hz
        num_samples = 1000  # Number of samples to read per channel
        scan_rate = 25000   # Samples per second

        channel_rms_values = {}
        
        for channel in channels:
            try:
                # Convert channel name to address
                channel_address = ljm.nameToAddress(channel)[0]

                # Start the stream for the specific channel
                scan_rate_actual = ljm.eStreamStart(self.handle, num_samples, 1, [channel_address], scan_rate)
                logging.info(f"Streaming {num_samples} samples for {channel} at {scan_rate_actual} samples per second")

                # Read streamed data
                data = ljm.eStreamRead(self.handle)[0]  # Get the data

                # Stop the stream
                ljm.eStreamStop(self.handle)
                logging.info(f"Stream stopped for {channel}")

                # Calculate RMS for the streamed data
                channel_rms_values[channel] = self._calculate_rms(data)

            except ljm.LJMError as e:
                raise Exception(f"Failed to stream samples for {channel}: {e}")

        return channel_rms_values

    def _calculate_rms(self, values):
        """Calculate the RMS of a list of values."""
        square_sum = sum([value ** 2 for value in values])
        mean_square = square_sum / len(values)
        rms = math.sqrt(mean_square)
        return rms
