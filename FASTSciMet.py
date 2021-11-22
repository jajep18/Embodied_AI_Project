#!/usr/bin/env python3
import ev3dev.ev3 as ev3 
from time import sleep


btn = ev3.Button()
mLeft   = ev3.LargeMotor('outD') # Left motor
mRight  = ev3.LargeMotor('outA') # Right motor
mLeft.run_direct()
mRight.run_direct()

DRIVE_V = 100

def DRIVE(speed):
    mLeft.duty_cycle_sp     = speed
    mRight.duty_cycle_sp    = speed

while True:

    if btn.down:
        ev3.Sound.beep().wait()
        sleep(2)
        DRIVE(DRIVE_V)
    if (btn.right or btn.left):
        DRIVE(0)
        ev3.Sound.beep().wait()
    if btn.backspace:
        DRIVE(0)
        ev3.Sound.beep().wait()
        ev3.Sound.beep().wait()
        exit()