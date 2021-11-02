#!/usr/bin/env python3
import ev3dev.ev3 as ev3 
from time import sleep
import signal

btn = ev3.Button()
sLight = ev3.LightSensor('in1') # Left color sensor

while True:
    # - - - LOAD SENSOR VALUES - - -
    sLight_val= sLight.value()

    print("Sensor value: " + str(sLight_val))

    if btn.any():
        ev3.Sound.beep().wait()
        exit()