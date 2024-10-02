# LabJack-Driver

This is a driver for the LabJack T7. Currently, this hardware only reads the analog inputs of the LabJack over Ethernet.

## Capabilities
- **Set Voltage Range**: Supports setting the voltage range for analog input channels (AIN) to ±10V, ±1V, ±0.1V, or ±0.01V.
- **Single-Ended (GND-Referenced) Measurements**: Perform single-ended readings, where the input is referenced to GND.
- **Differential Measurements**: Perform differential readings, where one analog input is referenced to another input (e.g., AIN2 is referenced to AIN3).
- The structure of this library is identical to that of [ADAM-driver](https://github.com/spanio/ADAM-driver) and [NIDAQ-driver](https://github.com/spanio/NIDAQ-driver), allowing easy integration into [nexo](https://github.com/spanio/nexo) and [ScriptSynth](https://github.com/spanio/ScriptSynth).

## Requirements



# Requirements
```
pip install LabJackPython ljm
```

# Documentation

## Differential vs. Single-Ended Measurements

- **Single-Ended (GND-Referenced) Measurements**: 
  - In a single-ended measurement, the analog input is referenced to GND (ground). For example, reading AIN0 with a GND reference means the LabJack measures the voltage difference between AIN0 and GND.
  - To configure a channel for single-ended mode, set the `AIN#_NEGATIVE_CH` to `199` (which corresponds to GND).

- **Differential Measurements**: 
  - In a differential measurement, the voltage difference between two analog inputs is measured. For example, you can measure AIN2 referenced to AIN3 by setting the `AIN2_NEGATIVE_CH` to 3 (AIN3).
  - This mode is useful when you want to measure signals that are not referenced to GND but instead to another input channel.
  - To configure a channel for differential mode, set the `AIN#_NEGATIVE_CH` to the index of the negative channel (e.g., `AIN2_NEGATIVE_CH = 3` for differential measurement between AIN2 and AIN3).

### Example Configuration:
- **Single-Ended Reading (AIN0-GND)**:
  ```python
  labjack.set_range(0, "10V")
  labjack.configure_measurement_type(0, measurement_type="single-ended")
- **Differential Reading (AIN0-GND)**:
  ```python
  labjack.set_range(2, "10V")
  labjack.configure_measurement_type(2, measurement_type="differential", differential_negative_channel=3)
  ```

# Example Usage
```python
from LabjackClient import LabJackT7Driver

# LabJack IP Address
LABJACK_IP = "172.18.120.132"

# Initialize the LabJackT7Driver with the IP address
client = LabJackT7Driver(ip_address=LABJACK_IP)

try:
    # Configure the voltage range for AIN0 to ±10V and set the negative channel to GND (single-ended)
    client.set_range(0, "10V")
    client.configure_measurement_type(0, measurement_type="single-ended")

    # Configure AIN2 to take a differential reading using AIN3 as the negative channel
    client.set_range(2, "10V")
    client.configure_measurement_type(2, measurement_type="differential", differential_negative_channel=3)

    # Read analog input values from the first 4 channels
    analog_values = client.read_samples([f"AIN{i}" for i in range(4)])
    print(analog_values)

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()

```
# Setup

The Labjack device must be connected via Ethernet; the IP should be automatically assigned, but you will need to _find_ the IP address. To do this, [download Kipling](https://github.com/labjack/labjack_kipling), the official configuration utility. After running this, you will find something like this:

![Kipling screenshot](/Docu/LabjackKipling.PNG)

The Ethernet IP is shown in the configuration utility. Write down the IP address.