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
BASE_SPEED = -30
TURN_SPEED = -80

# - - - - - - - - - - SETUP SENSORS - - - - - - - - - -
btn     = ev3.Button()           # Control block buttons
#sTouch = ev3.TouchSensor('in2')
#sGyro   = ev3.GyroSensor('in1')  # Gyro sensor
sColorR = ev3.ColorSensor('in4') # Right color sensor
sColorL = ev3.ColorSensor('in1') # Left color sensor

#Put gyro in ANGLE mode
#sGyro.mode='GYRO-RATE'
#units = sGyro.units

# Reflected light, value between 0 and 100, ~80 white, ~5 black
sColorR.mode='COL-REFLECT'
sColorL.mode='COL-REFLECT'
sColorVal = [sColorL.value(), sColorR.value()]

mu = 7

# - - - - - - - - - - CONTROL LOOP - - - - - - - - - -
while True:
    # - - - LOAD SENSOR VALUES - - -
    #angle = sGyro.value()
    #print(str(angle) + " " + units)
    sColorVal_prev = sColorVal
    sColorVal = [sColorL.value(), sColorR.value()]
    print("Color sensor left: " + str(sColorVal[0]) + "    right: " + str(sColorVal[1]))

    # - - - LINE FOLLOWING - - -
    #sColorVal[0] = A
    #sColorVal[1] = B
    w_a = mu * sColorVal[0]/100 * (sColorVal[1] - sColorVal_prev[1])/100
    w_b = mu * sColorVal[1]/100 * (sColorVal[0] - sColorVal_prev[0])/100
    Y_R = w_a * sColorVal[0]
    Y_L = w_b * sColorVal[1]
    print(str(sColorVal[0]) + " " +str(sColorVal[1]) + " " +str(w_a) + " " + str(w_b) + " " + str(Y_R) + " " + str(Y_L))

    mLeft.duty_cycle_sp = -15 - Y_L
    mRight.duty_cycle_sp = -15 - Y_R

    sleep(0.5)
    if btn.any():
        ev3.Sound.beep().wait()
        mRight.duty_cycle_sp = 0
        mLeft.duty_cycle_sp = 0
        #mClaw.duty_cycle_sp = 0
        exit()