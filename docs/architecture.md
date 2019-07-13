# Purpose

The purpose of this project is to provide a simple interface for other embedded devices (ex: Raspberry Pi) to communicate with to read time-series sensor data specific to soil-based measurements.

# How does it work?

1. This device runs continously waiting for you to pull data from it.

2. When you pull data, it will send you a ``JSON`` formatted object with all the time series data.

3. To pull data, you must first connect to the **Mikapod Soil (Arduino)** device with a USB cable.

4. Once connected, you use **serial usb communication** to read data from the device and write commands to the device.

5. Once your device recieves the ``JSON`` data, you do what you want with the data.


# Why did you choose Arduino?

The **Arduino** platform has a wonderful ecosystem of open-source hardware with libraries. Our goal is to take advantage of the libraries the hardware manufacturers wrote and not worry about the complicated implementation details.

# How does the data output look like?

When the device is ready to be used, you will see this output:

```json
{"status":"READY","runtime":2,"id":1,"sensors":["humidity","temperature","pressure","illuminance","soil"]}
```

When you poll the device for data, you will see this output:

```json
{"status":"RUNNING","runtime":24771,"id":2,"humidity":{"value":47.92456,"unit":"%","status":1,"error":""},"temperature_primary":{"value":80.47031,"unit":"F","status":1,"error":""},"pressure":{"value":0,"unit":"Pa","status":1,"error":""},"temperature_secondary":{"value":78.2375,"unit":"F","status":1,"error":""},"altitude":{"value":80440.25,"unit":"ft","status":1,"error":""},"illuminance":{"value":0.040305,"unit":"V","status":1,"error":""},"soil_moisture":{"value":697,"unit":"SIG","status":1,"error":""}}
```

# How is this connected to the Mikaponics ecosystem?

This is the codebase used by the **Mikapod Soil** device that we sell. The realtime data is consumed by the [Mikapod Soil (Raspberry Pi)](https://github.com) device which will be uploaded to the [Mikaponics API web-service](https://github.com/mikaponics/mikaponics-back).


# Why should I use it?
The **Mikapod Soil (Arduino)** is a easy to connect and read realtime time-series data using any language that supports **serial communication over USB**.

If you are looking to get plant data pertainting to soil-based sensors, this is the project to use.
