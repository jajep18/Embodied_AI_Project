#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from time import sleep
import signal

#- - - - - - - - - - SETUP MOTORS - - - - - - - - - -
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
TARGET = 0 #(BLACK + WHITE ) / 2  # = 80 + 10 / 2 = 45
#THRESHOLD_1 = ((WHITE - BLACK) / 3) + BLACK
#THRESHOLD_2 = WHITE - ((WHITE - BLACK) / 3)

# - - - - - - - - - - PID CONTROL - - - - - - - - - -
# GAINS
Kp = 6.6161  #0.42
Ki = 53.112  #0.0008
Kd = 0.20553 #0.001
# Components
integral   = 0
derivative = 0
last_error = 0
error      = 0
error_sum  = 0
# - - - - - - - - - - CONTROL LOOP - - - - - - - - - -
while True:
    # - - - LOAD SENSOR VALUES - - -
    sColorL_val= sColorL.value()
    sColorR_val= sColorR.value()
    print("Left sensor: " + str(sColorL_val) + " Right sensor " + str(sColorR_val))
    # PID Line Follower

    com_input = (sColorL_val - sColorR_val) / 2 # If negative go left. If Possitive go right
    #print("Combined input =" + str(com_input))
    error = com_input - TARGET
    integral = integral + error
    derivative = error - error_sum #Current error - last 10 error values
    
    #Update error array
    last_error[9] = last_error[8]
    last_error[8] = last_error[7]
    last_error[7] = last_error[6]
    last_error[6] = last_error[5]
    last_error[5] = last_error[4]
    last_error[4] = last_error[3]
    last_error[3] = last_error[2]
    last_error[2] = last_error[1]
    last_error[1] = last_error[0]   
    last_error[0] = error           #Current error

    error_sum = 0
    for i in range( 0 , len(last_error)-1 ):
        error_sum -= last_error[i] - last_error[i+1]
    

    turn_val = Kp * error + Ki * integral + Kp * derivative
    #print("Turn value: " +str(turn_val))
    mRight_val = DRIVE_SPEED + int(turn_val)
    mLeft_val = DRIVE_SPEED - int(turn_val)
    #print("mRight: " + str(mRight_val) + "  mLeft: " + str(mLeft_val))
    #mRight.duty_cycle_sp = mRight_val
    #mLeft.duty_cycle_sp  = mLeft_val


    sleep(0.01)
    if btn.any():
        ev3.Sound.beep().wait()
        mRight.duty_cycle_sp = 0
        mLeft.duty_cycle_sp = 0
        #mClaw.duty_cycle_sp = 0
        exit()
