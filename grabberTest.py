#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from time import sleep
import signal

#sColorTouch = ev3.ColorSensor('in1') # Touch color sensor (claw)
btn     = ev3.Button()           # Control block buttons
mClaw  = ev3.LargeMotor('outB') # Claw motor

#sColorTouch.mode='COL-COLOR'
grap = -85
release = -grap

mClaw.run_direct()


while(True):
    

    mClaw.run_to_rel_pos(position_sp=grap, speed_sp=200, stop_action="hold")

    sleep(2)   # Give the motor time to move
    mClaw.run_to_rel_pos(position_sp=release, speed_sp=100, stop_action="coast")
    sleep(2)

    if btn.any():
        ev3.Sound.beep().wait()
        mClaw.duty_cycle_sp = 0
        exit()


