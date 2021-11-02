#!/usr/bin/env python3
import ev3dev.ev3 as ev3 
from time import sleep
import signal

btn = ev3.Button()
sLight = ev3.LightSensor('in2') # Left color sensor
mClaw  = ev3.LargeMotor('outB') # Claw motor
mClaw.run_direct()

grap = -85
release = -grap


while True:
    # - - - LOAD SENSOR VALUES - - -
    sLight_val= sLight.value()

    print("Sensor value: " + str(sLight_val))
    if sLight_val >= 500:
        mClaw.run_to_rel_pos(position_sp=grap, speed_sp=200, stop_action="hold")
        sleep(5)   # Give the motor time to move
        mClaw.run_to_rel_pos(position_sp=release, speed_sp=100, stop_action="coast")
        sleep(2)

    if btn.any():
        ev3.Sound.beep().wait()
        exit()