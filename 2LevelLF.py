#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from time import sleep
import signal

# - - - - - - - - - - SETUP MOTORS - - - - - - - - - -
mRight = ev3.LargeMotor('outA')  # Right wheel motor
mLeft  = ev3.LargeMotor('outD')  # Left wheel motor
#mClaw  = ev3.MediumMotor('outC') # Claw motor

mRight.run_direct()
mLeft.run_direct()
#mClaw.run_direct()

NONTURN_SPEED = -30
TURN_SPEED = -80
DRIVE_SPEED = -65

# - - - - - - - - - - SETUP SENSORS - - - - - - - - - -
btn     = ev3.Button()           # Control block buttons
#sTouch = ev3.TouchSensor('in2')
#sGyro   = ev3.GyroSensor('in1')  # Gyro sensor
sColorR = ev3.ColorSensor('in4') # Right color sensor
sColorL = ev3.ColorSensor('in1') # Left color sensor


# Reflected light, value between 0 and 100, ~80 white, ~5 black
sColorR.mode='COL-REFLECT'
sColorL.mode='COL-REFLECT'

WHITE = 80
BLACK = 10
#THRESHOLD = (BLACK + WHITE ) / 2
THRESHOLD = 70

# - - - - - - - - - - CONTROL LOOP - - - - - - - - - -
while True:
    # - - - LOAD SENSOR VALUES - - -
    sColorL_val= sColorL.value()
    
    # 2-Level Line follower
    if sColorL_val <= THRESHOLD:
        #black line
        mLeft.duty_cycle_sp = DRIVE_SPEED
        mRight.duty_cycle_sp = 0
    else:
        #white zone
        mRight.duty_cycle_sp = DRIVE_SPEED
        mLeft.duty_cycle_sp = 0

    #sleep(0.001)
    if btn.any():
        ev3.Sound.beep().wait()
        mRight.duty_cycle_sp = 0
        mLeft.duty_cycle_sp = 0
        #mClaw.duty_cycle_sp = 0
        exit()
