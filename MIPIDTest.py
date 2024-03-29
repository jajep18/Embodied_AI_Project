#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from time import sleep
import signal
import array

#- - - - - - - - - - SETUP MOTORS - - - - - - - - - -
mRight = ev3.LargeMotor('outA')  # Right wheel motor
mLeft  = ev3.LargeMotor('outD')  # Left wheel motor
mClaw  = ev3.LargeMotor('outC') # Claw motor

mRight.run_direct()
mLeft.run_direct()
mClaw.run_direct()

NONTURN_SPEED = 30
TURN_SPEED  = 60
DRIVE_SPEED = 30
GRAB_ANGLE  = 100 #85
RELEASE_ANGLE = -GRAB_ANGLE

# - - - - - - - - - - SETUP SENSORS - - - - - - - - - -
btn     = ev3.Button()           # Control block buttons
#sGyro   = ev3.GyroSensor('in1')  # Gyro sensor
sColorR = ev3.ColorSensor('in4') # Right color sensor
sColorL = ev3.ColorSensor('in1') # Left color sensor
sLightC = ev3.LightSensor('in3') # Light sensor for claw


# Reflected light, value between 0 and 100, ~80 white, ~5 black
sColorR.mode='COL-REFLECT'
sColorL.mode='COL-REFLECT'

WHITE = 80
BLACK = 10
TARGET = -5.5 #(BLACK + WHITE ) / 2  # = 80 + 10 / 2 = 45
#THRESHOLD_1 = ((WHITE - BLACK) / 3) + BLACK
#THRESHOLD_2 = WHITE - ((WHITE - BLACK) / 3)

# - - - - - - - - - - PID CONTROL - - - - - - - - - -
# GAINS
Kp = 3.3#6.6161  #0.42
Ki = 0.053112  #0.0008
Kd = 1#= 0.20553 #0.001
# Components
integral   = 0
derivative = 0
last_error = [0] * 10
error      = 0
error_sum  = 0
integral_clamp = 20

# - - - - - - - - - - FUNCTIONS - - - - - - - - - -
def setMotorSP(motorHandle, sp_input): 
    #FLIPS MOTOR COMMAND BECAUSE OF MOUNTED DIRECTION
    sp_input_n = - sp_input
    if(sp_input_n > 100):
        motorHandle.duty_cycle_sp = 100
        print("Upper limit motor cap exceeded")
    elif(sp_input_n < -100):
        motorHandle.duty_cycle_sp = -100
        print("Lower limit motor cap exceeded")
    else:
        motorHandle.duty_cycle_sp = sp_input_n

# - - - - - - - - - - CONTROL LOOP - - - - - - - - - -
while True:
    # - - - LOAD SENSOR VALUES - - -
    sColorL_val= sColorL.value()
    sColorR_val= sColorR.value()
    

    # - - - - - - - - - - PID Line Follower - - - - - - - - - -
    com_input = (sColorL_val - sColorR_val) / 10 #/2# If negative go left. If Positive go right
    #print("Combined input =" + str(com_input))
    error = com_input - TARGET
    integral = integral + error
    derivative = error - error_sum #Current error - last 10 error values

    print("Left sensor: " + str(sColorL_val) + " Right sensor " + str(sColorR_val) + " com_input: " + str(com_input))
    
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

    ##################### Sum over error ###############################################
    error_sum = 0
    for i in range( 0 , len(last_error)-1 ):
        error_sum -= last_error[i] - last_error[i+1]
    
    ##################### Integrator clamping to remove windup #########################
    if(abs(integral) > integral_clamp and integral > 0):
        integral = integral_clamp   

    elif(abs(integral) > integral_clamp and integral < 0):
        integral = -integral_clamp

    #turn_val = Kp * error + Ki * integral + Kd * derivative
    turn_val = Kp * error + Ki * integral + Kd * derivative
    print("PID-P(error): " + str(error) + " I: " + str(integral) + " D: " + str(derivative))
 


    print("Turn value: " + str(turn_val))
    mRight_val = DRIVE_SPEED + int(turn_val)
    mLeft_val = DRIVE_SPEED - int(turn_val)
    #print("mRight: " + str(mRight_val) + "  mLeft: " + str(mLeft_val))
    #mRight.duty_cycle_sp = mRight_val
    #mLeft.duty_cycle_sp  = mLeft_val
    setMotorSP(mRight, mRight_val)
    setMotorSP(mLeft, mLeft_val)

    #sleep(1)
    sleep(0.01)
    ##################### If button pressed, end program ###############################
    if btn.any(): ######## 
        ev3.Sound.beep().wait()
        mRight.duty_cycle_sp = 0
        mLeft.duty_cycle_sp = 0
        #mClaw.duty_cycle_sp = 0
        exit()

    ##################### Grab can in front of robot ###############################
    if sLightC.value() >= 500:
        mRight.duty_cycle_sp = 0
        mLeft.duty_cycle_sp = 0
        mClaw.run_to_rel_pos(position_sp=GRAB_ANGLE, speed_sp=200, stop_action="hold")
        sleep(2)   # Give the motor time to move
        mClaw.run_to_rel_pos(position_sp=RELEASE_ANGLE, speed_sp=100, stop_action="coast")
        sleep(2)
        #TODO: Add turning around - Dont let go of can again
