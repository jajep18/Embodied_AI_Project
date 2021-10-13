#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from time import sleep
import signal

btn = ev3.Button()

mA = ev3.LargeMotor('outA')
mD = ev3.LargeMotor('outD')
#test

BASE_SPEED = -10

mA.run_direct()
mD.run_direct()

while True:
    mA.duty_cycle_sp = BASE_SPEED
    #mB.duty_cycle_sp = BASE_SPEED
    #mC.duty_cycle_sp = BASE_SPEED
    mD.duty_cycle_sp = BASE_SPEED
        
    if btn.any():
        ev3.Sound.beep().wait()
        BASE_SPEED = BASE_SPEED - 10
        if BASE_SPEED == -90:
            ev3.Sound.beep().wait()
            mA.duty_cycle_sp = 0
            mD.duty_cycle_sp = 0

            exit()