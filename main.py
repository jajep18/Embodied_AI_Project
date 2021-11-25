#!/usr/bin/env python3
from ev3dev.core import GyroSensor
import ev3dev.ev3 as ev3
from time import sleep
import signal
import array

#- - - - - - - - - - SETUP MOTORS - - - - - - - - - -
mRight = ev3.LargeMotor('outD')  # Right wheel motor
mLeft  = ev3.LargeMotor('outA')  # Left wheel motor
mClaw  = ev3.LargeMotor('outC') # Claw motor



mRight.run_direct()
mLeft.run_direct()
mClaw.run_direct()

NONTURN_SPEED = 30
TURN_SPEED  = 60
DRIVE_SPEED = 40
GRAB_ANGLE  = -100 #85
RELEASE_ANGLE = -GRAB_ANGLE

# - - - - - - - - - - SETUP SENSORS - - - - - - - - - -
btn     = ev3.Button()           # Control block buttons
sGyro   = ev3.GyroSensor('in2')  # Gyro sensor
sColorR = ev3.ColorSensor('in4') # Right color sensor
sColorL = ev3.ColorSensor('in1') # Left color sensor
sLightC = ev3.LightSensor('in3') # Light sensor for claw



# Reflected light, value between 0 and 100, ~80 white, ~5 black
sColorR.mode='COL-REFLECT'
sColorL.mode='COL-REFLECT'
sGyro.mode='GYRO-RATE'

sleep(0.5)

WHITE = 80
BLACK = 10
TARGET = 0 #(BLACK + WHITE ) / 2  # = 80 + 10 / 2 = 45

gyro_offset = sGyro.value()

# - - - - - - - - - - PID CONTROL - - - - - - - - - -
# GAINS
d_T = 0.0141 #[ms]
K_c = 50
P_c = 0.75 
Kp =  25#30  #0.6 * K_c                  #12.2 #6.6161  #0.42
Ki =  2#1.128#1.128  #2 * Kp * d_T / P_c         #2.5#1.3#1.5#3#0.53112  #0.0008
Kd =  5#10#199.47  #Kp * P_c / (8*d_T)         #4.84
BACKWARDS_GAIN = 1# 1.2             # 2.2#2.5
# Components
integral   = 0
derivative = 0
last_error = 0
error      = 0
integral_clamp = 10
error_max = 1.8

# - - - - - - - - - - FUNCTIONS - - - - - - - - - -
def setMotorSP(motorHandle, sp_input): 
    #FLIPS MOTOR COMMAND BECAUSE OF MOUNTED DIRECTION
    sp_input_n = - sp_input
    if(sp_input_n > 100):
        motorHandle.duty_cycle_sp = 100
    elif(sp_input_n < -100):
        motorHandle.duty_cycle_sp = -100
    else:
        motorHandle.duty_cycle_sp = sp_input_n

# - - - - - - - - - - CONTROL LOOP - - - - - - - - - -

ev3.Sound.beep().wait()
while True:
    gyro_val = sGyro.value()-gyro_offset
    print(str(gyro_val))
    
    # - - - LOAD SENSOR VALUES - - -
    sColorL_val= sColorL.value()
    sColorR_val= sColorR.value()
    last_error = error # Save last error for derivative

    # - - - - - - - - - - PID Line Follower - - - - - - - - - -
    # INPUT / ERROR = [-5;5]
    com_input = (sColorR_val - sColorL_val) / 20 #/2# If negative go left. If Positive go right
    error = com_input - TARGET
    
    integral = integral * (3/4) + error
    derivative = error - last_error #Current error - last 10 error values
    # if abs(error) > abs(error_max):
    #     error_max = error
    #print("Error: " + str(error) +" sL: " + str(sColorL_val )+ " sR: " + str(sColorR_val) + " Emax: " + str(error_max))
    
    ##################### Integrator clamping to remove windup #########################
    if(abs(integral) > integral_clamp and integral > 0):
        integral = integral_clamp

    elif(abs(integral) > integral_clamp and integral < 0):
        integral = -integral_clamp


    turn_val = Kp * error + Ki * integral + Kd * derivative

    if abs(error) > error_max:
        error = error_max * error/abs(error)

    
    DRIVE_SPEED_corr = DRIVE_SPEED * (1 - abs(error)/error_max)
    
     #* (abs(int(integral))-integral_clamp)/(-20)
    #mRight_val =  DRIVE_SPEED_corr + int(turn_val)
    #mLeft_val = DRIVE_SPEED_corr - int(turn_val)
    
    if turn_val >= 0:
        mRight_val = DRIVE_SPEED_corr + int(turn_val) 
        mLeft_val  = DRIVE_SPEED_corr - int(turn_val) * BACKWARDS_GAIN #(1 + ( BACKWARDS_GAIN*abs(error) ) / 5)
    else:
        mRight_val = DRIVE_SPEED_corr + int(turn_val) * BACKWARDS_GAIN #(1 + ( BACKWARDS_GAIN*abs(error) ) / 5)
        mLeft_val  = DRIVE_SPEED_corr - int(turn_val)
    #print("mRight: " + str(mRight_val) + "  mLeft: " + str(mLeft_val))

    #setMotorSP(mRight, mRight_val)
    #setMotorSP(mLeft, mLeft_val)

    
    #sleep(0.001)
    ##################### If button pressed, end program ###############################
    if btn.any(): ######## 
        ev3.Sound.beep().wait()
        mRight.duty_cycle_sp = 0
        mLeft.duty_cycle_sp = 0
        #mClaw.duty_cycle_sp = 0
        exit()

    ##################### Grab can in front of robot ###############################
    # if sLightC.value() >= 500:
    #     mRight.duty_cycle_sp = 0
    #     mLeft.duty_cycle_sp = 0
    #     mClaw.run_to_rel_pos(position_sp=GRAB_ANGLE, speed_sp=200, stop_action="hold")
    #     sleep(2)   # Give the motor time to move
    #     mClaw.run_to_rel_pos(position_sp=RELEASE_ANGLE, speed_sp=100, stop_action="coast")
    #     sleep(2)
    #     #TODO: Add turning around - Dont let go of can again
# setMotorSP(mRight, 0)
# setMotorSP(mLeft, 0)
# ev3.Sound.beep().wait()