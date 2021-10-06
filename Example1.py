#!/usr/bin/env python3
from ev3dev.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev.sensor.lego import ColorSensor
from ev3dev.button import Button
from time import sleep

btn = Button() # we will use any button to stop script
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Connect an EV3 color sensor to any sensor port.
cl = ColorSensor()

while not btn.any():    # exit loop when any button pressed
    # if we are over the black line (weak reflection)
    if cl.reflected_light_intensity<30:   
        # medium turn right
        tank.on(left_speed=50, right_speed=0)
    
    else:   # strong reflection (>=30) so over white surface
        # medium turn left
        tank.on(left_speed=0, right_speed=50)
    
    sleep(0.1) # wait for 0.1 seconds