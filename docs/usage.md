# Serial Monitor
The **Arduino IDE** comes with a serial monitor. You can use this device and submit requests to the device to pull latest time-series data from our sensors.

![Soil Moisture](img/hardware/serial_monitor_example.png)
Example output of Serial Monitor

# Python
The following instructions will demonstrate how to communicate with the device.

1. Run the following commands to setup our script which will communicate with the ``Arduino`` computer.

        $ cd ~/
        $ virtualenv -p python3.7 env
        $ source env/bin/activate
        $ pip install pyserial
        $ cat > arduino_reader.py

2. Copy and paste this code.

        ```python
        from serial import Serial
        from time import sleep

        port = "/dev/ttyACM0" # PLEASE CHANGE THIS TO WHATEVER PORT YOUR DEVICE IS ON.
        ser = Serial(port, 9600, timeout=None)

        sleep(2) # wait for Arduino

        while True:
            byte_data = ser.readline()
            sleep(2);
            print(byte_data) # LEARN https://stackoverflow.com/questions/24074914/python-to-arduino-serial-read-write

            string_data = byte_data.decode('UTF-8') # https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal#6273618
            print(string_data)
        ```

3. Run the script!

        $ python3 arduino_reader.py

5. You should get running code. For more information please [visit this link](https://oscarliang.com/connect-raspberry-pi-and-arduino-usb-cable/) for more details.
