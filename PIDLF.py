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
TURN_SPEED = -60
DRIVE_SPEED = -50

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
TARGET = (BLACK + WHITE ) / 2
#THRESHOLD_1 = ((WHITE - BLACK) / 3) + BLACK
#THRESHOLD_2 = WHITE - ((WHITE - BLACK) / 3)

# - - - - - - - - - - PID CONTROL - - - - - - - - - -
# GAINS
Kp = 0.42
Ki = 0.0008
Kd = 0.001
# Components
integral   = 0
derivative = 0
last_error = 0
error      = 0

# - - - - - - - - - - CONTROL LOOP - - - - - - - - - -
while True:
    # - - - LOAD SENSOR VALUES - - -
    sColorL_val= sColorL.value()
    
    # PID Line Follower
    error = sColorL_val - TARGET
    integral = integral + error
    derivative = error - last_error
    last_error = error

    turn_val = Kp * error + Ki * integral + Kp * derivative
    mRight_val = DRIVE_SPEED + int(turn_val)
    mLeft_val = DRIVE_SPEED - int(turn_val)
    print("mRight: " + str(mRight_val) + "  mLeft: " + str(mLeft_val))
    mRight.duty_cycle_sp = mRight_val
    mLeft.duty_cycle_sp  = mLeft_val


    sleep(0.01)
    if btn.any():
        ev3.Sound.beep().wait()
        mRight.duty_cycle_sp = 0
        mLeft.duty_cycle_sp = 0
        #mClaw.duty_cycle_sp = 0
        exit()
