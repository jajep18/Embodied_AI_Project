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
DRIVE_SPEED = 40
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
TARGET = 0 #(BLACK + WHITE ) / 2  # = 80 + 10 / 2 = 45
#THRESHOLD_1 = ((WHITE - BLACK) / 3) + BLACK
#THRESHOLD_2 = WHITE - ((WHITE - BLACK) / 3)

# - - - - - - - - - - PID CONTROL - - - - - - - - - -
# GAINS
<<<<<<< HEAD
Kp = 10.2 #6.6161  #0.42
Ki = 1.3#1.5#3#0.53112  #0.0008
Kd = 0.41#0.20553 #0.001
BACKWARDS_GAIN = 2.5
=======
Kp = 6.6161  #0.42
Ki = 2#0.53112  #0.0008
Kd = 0.20553 #0.001
>>>>>>> 4b59d8457e855cd3422f529fcb3abbce6d28f6d0
# Components
integral   = 0
derivative = 0
last_error = 0
error      = 0
<<<<<<< HEAD
integral_clamp = 5
=======
integral_clamp = 20
>>>>>>> 4b59d8457e855cd3422f529fcb3abbce6d28f6d0

# - - - - - - - - - - FUNCTIONS - - - - - - - - - -
def setMotorSP(motorHandle, sp_input): 
    #FLIPS MOTOR COMMAND BECAUSE OF MOUNTED DIRECTION
    sp_input_n = - sp_input
    if(sp_input_n > 100):
        motorHandle.duty_cycle_sp = 100
        #print("Upper limit motor cap exceeded")
    elif(sp_input_n < -100):
        motorHandle.duty_cycle_sp = -100
        #print("Lower limit motor cap exceeded")
    else:
        motorHandle.duty_cycle_sp = sp_input_n

# - - - - - - - - - - CONTROL LOOP - - - - - - - - - -
while True:
    # - - - LOAD SENSOR VALUES - - -
    sColorL_val= sColorL.value()
    sColorR_val= sColorR.value()
    last_error = error # Save last error for derivative

    # - - - - - - - - - - PID Line Follower - - - - - - - - - -
<<<<<<< HEAD
    # INPUT / ERROR [-5;5]
    com_input = (sColorL_val - sColorR_val) / 20 #/2# If negative go left. If Positive go right
    #print("Combined input =" + str(com_input))
    error = com_input - TARGET
    integral = integral * (4/5) + error
=======
    com_input = (sColorL_val - sColorR_val) / 10 #/2# If negative go left. If Positive go right
    #print("Combined input =" + str(com_input))
    error = com_input - TARGET
    integral = integral + error
>>>>>>> 4b59d8457e855cd3422f529fcb3abbce6d28f6d0
    derivative = error - last_error #Current error - last 10 error values
    #print("Left sensor: " + str(sColorL_val) + " Right sensor " + str(sColorR_val) + " com_input: " + str(com_input))
    
    
    
    ##################### Integrator clamping to remove windup #########################
    if(abs(integral) > integral_clamp and integral > 0):
        integral = integral_clamp

    elif(abs(integral) > integral_clamp and integral < 0):
        integral = -integral_clamp

    #turn_val = Kp * error + Ki * integral + Kd * derivative
    turn_val = Kp * error + Ki * integral + Kd * derivative
    #print("PID-P(error): " + str(error) + " I: " + str(integral) + " D: " + str(derivative))
<<<<<<< HEAD

    #print("Turn value: " + str(turn_val))
    DRIVE_SPEED_corr = DRIVE_SPEED #* (abs(int(integral))-integral_clamp)/(-20)
    #mRight_val =  DRIVE_SPEED_corr + int(turn_val)
    #mLeft_val = DRIVE_SPEED_corr - int(turn_val)
    
    if turn_val >= 0:
        mRight_val = DRIVE_SPEED_corr + int(turn_val) 
        mLeft_val  = DRIVE_SPEED_corr - int(turn_val) * BACKWARDS_GAIN
    else:
        mRight_val = DRIVE_SPEED_corr + int(turn_val) * BACKWARDS_GAIN
        mLeft_val  = DRIVE_SPEED_corr - int(turn_val)
=======
 


    #print("Turn value: " + str(turn_val))
    DRIVE_SPEED_corr = DRIVE_SPEED * (abs(int(integral))-integral_clamp)/(-20)
    mRight_val =  DRIVE_SPEED_corr + int(turn_val)
    mLeft_val = DRIVE_SPEED_corr - int(turn_val)
>>>>>>> 4b59d8457e855cd3422f529fcb3abbce6d28f6d0
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
<<<<<<< HEAD
        #TODO: Add turning around - Dont let go of can again
=======
        #TODO: Add turning around - Dont let go of can again
>>>>>>> 4b59d8457e855cd3422f529fcb3abbce6d28f6d0
