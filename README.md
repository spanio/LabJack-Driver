# LabJack-Driver

This is a driver for the LabJack T7. Currently, this hardware only reads the analog inputs of the LabJack. This driver only supports reading data over Ethernet.

Capabilities include: setting the voltage range for the AIN (+/- 10V, +/- 1V, +/- 0.1V, +/- 0.01V), and setting the reference (AIN or GND).

Structure of this library is identical to that of [ADAM-driver](https://github.com/spanio/ADAM-driver) and [NIDAQ-driver](https://github.com/spanio/NIDAQ-driver), to allow for integration into [nexo](https://github.com/spanio/nexo) and [ScriptSynth](https://github.com/spanio/ScriptSynth).


# Example
```python
from Python import Python something something here
```
# Setup

The Labjack device must be connected via Ethernet; the IP should be automatically assigned, but you will need to _find_ the IP address. To do this, [download Kipling](https://github.com/labjack/labjack_kipling), the official configuration utility. After running this, you will find something like this:

![Kipling screenshot](/Docu/LabjackKipling.PNG)

The Ethernet IP is shown in the configuration utility. Write down the IP address.