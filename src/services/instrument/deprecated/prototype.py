#!/usr/bin/python
import json
from serial import Serial
from time import sleep

RX_BYTE = '1'.encode('UTF-8')

# LEARN https://stackoverflow.com/questions/24074914/python-to-arduino-serial-read-write

'''
Wait until our computer can connect to the external device over serial USB
communication to begin running our program.
'''
port = "/dev/cu.usbmodem1D132101"
ser = Serial(port, 9600, timeout=10)
sleep(2) # wait for Arduino


'''
Wait until the external device is ready.
'''
while True:
    byte_data = ser.readline()
    json_string = byte_data.decode('UTF-8') # https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal#6273618
    if len(json_string) > 0:
        if "READY" in str(json_string):
            # obj = json.loads(json_string) # FOR DEBUGGING PURPOSES ONLY.
            # print("DEBUG:", obj)
            break

def print_output(readings):
    humidity = readings['humidity']
    print(humidity)
    illuminance = readings['illuminance']
    print(illuminance)
    pressure = readings['pressure']
    print(pressure)
    temperature = readings['temperature']
    print(temperature)

'''
Run event based polling.
'''
while True:
    # DEVELOPERS NOTE:
    # We need to send a single byte to the external device which will trigger
    # a polling event on external device.
    ser.write(RX_BYTE)
    byte_data = ser.readline()
    json_string = byte_data.decode('UTF-8') # https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal#6273618
    if len(json_string) > 0:
        parsed = json.loads(json_string)
        print(json.dumps(parsed, indent=4, sort_keys=True))
        print_output(parsed)
    sleep(5) # wait for Arduino
