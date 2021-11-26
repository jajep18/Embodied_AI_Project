#!/usr/bin/env python3
from ev3dev.core import GyroSensor
import ev3dev.ev3 as ev3
from time import sleep
import signal
import array
import csv

#- - - - - - - - - - SETUP MOTORS - - - - - - - - - -
mRight = ev3.LargeMotor('outD')  # Right wheel motor
mLeft  = ev3.LargeMotor('outA')  # Left wheel motor
mClaw  = ev3.LargeMotor('outC') # Claw motor

mRight.run_direct()
mLeft.run_direct()
mClaw.run_direct()

BASE_SPEED     = 40
UPHILL_SPEED   = 45
DOWNHILL_SPEED = 20
DRIVE_SPEED    = BASE_SPEED
GRAB_ANGLE     = -100 #85
RELEASE_ANGLE  = -GRAB_ANGLE
TURN_SPEED     = 40

# - - - - - - - - - - SETUP SENSORS - - - - - - - - - -
btn     = ev3.Button()           # Control block buttons
sGyro   = ev3.GyroSensor('in2')  # Gyro sensor
sColorR = ev3.ColorSensor('in4') # Right color sensor
sColorL = ev3.ColorSensor('in1') # Left color sensor
sLightC = ev3.LightSensor('in3') # Light sensor for claw

# Set sensor modes
sColorR.mode='COL-REFLECT'
sColorL.mode='COL-REFLECT'
sGyro.mode = 'GYRO-RATE'
sleep(0.5)
#gyro_offset = sGyro.value()
beta_gyro = 0.98

# - - - - - - - - - - DATA LOGS  - - - - - - - - - -
error_log       = []
integral_log    = []
sColorL_log     = []
sColorR_log     = []
sLightC_log     = []
sGyro_log       = []
GyroAng_log     = []


# - - - - - - - - - - PID CONTROL - - - - - - - - - -
# GAINS
Kp =  25#22.5#25#30  #0.6 * K_c                  #12.2 #6.6161  #0.42
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
#d_T = 0.0141 #[ms]
#K_c = 50
#P_c = 0.75 
TARGET = 0 #(BLACK + WHITE ) / 2  # = 80 + 10 / 2 = 45

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

# - - - - - - - - - - RAMP STATE SETUP - - - - - - - - - -
rs_flat = "flat"
rs_up   = "  up"
rs_down = "down"

ramp_speeds = {}
ramp_speeds[rs_flat] =  0
ramp_speeds[rs_up]   = 20
ramp_speeds[rs_down] =-20

ramp_state = rs_flat
GyroAng = 0

# - - - - - - - - - - CONTROL LOOP - - - - - - - - - -
ev3.Sound.beep().wait()
exit_cond = True
can_flag  = False

while exit_cond:
    # - - - LOAD SENSOR VALUES - - -
    sColorL_val = sColorL.value()
    sColorR_val = sColorR.value()
    sLightC_val = sLightC.value()
    sGyro_val   = sGyro.value() #- gyro_offset 
    last_error  = error # Save last error for derivative

    GyroAng = beta_gyro * GyroAng + (1 - beta_gyro) * sGyro_val #Bigbrain filter
    
    # - - - - - - - - - - PID Line Follower - - - - - - - - - -
    # INPUT / ERROR = [-5;5]
    com_input = (sColorR_val - sColorL_val) / 20 #/2# If negative go left. If Positive go right
    error = com_input - TARGET
    integral = integral * 0.90 + error 
    derivative = error - last_error #Current error - last 10 error values
    
    #Integrator clamping to remove windup
    if abs(integral) > integral_clamp:
        integral_clamp = integral_clamp * integral/abs(integral)

    # Calculate PID control output
    turn_val = Kp * error + Ki * integral + Kd * derivative

    ##################### Set motor speeds ###############################
    if ramp_state == rs_flat:
        if GyroAng > 10:
            ramp_state = rs_up
        elif GyroAng < -10:
            ramp_state = rs_down
    elif ramp_state == rs_up:
        if GyroAng < -10:
            ramp_state = rs_flat
            GyroAng = 0
    elif ramp_state == rs_down:
        if GyroAng > 10: 
            ramp_state = rs_flat
            GyroAng = 0

    # Error clamping to prevent driving backwards
    if abs(error) > error_max:
        error = error_max * error/abs(error)
    
    DRIVE_SPEED_corr = DRIVE_SPEED * (1 - abs(error)/error_max) + ramp_speeds[ramp_state]
    if turn_val >= 0:
        mRight_val = DRIVE_SPEED_corr + int(turn_val) 
        mLeft_val  = DRIVE_SPEED_corr - int(turn_val) * BACKWARDS_GAIN #(1 + ( BACKWARDS_GAIN*abs(error) ) / 5)
    else:
        mRight_val = DRIVE_SPEED_corr + int(turn_val) * BACKWARDS_GAIN #(1 + ( BACKWARDS_GAIN*abs(error) ) / 5)
        mLeft_val  = DRIVE_SPEED_corr - int(turn_val)
    #print("mRight: " + str(mRight_val) + "  mLeft: " + str(mLeft_val))

    setMotorSP(mRight, mRight_val)
    setMotorSP(mLeft, mLeft_val)
    print("RS: " + str(ramp_state) + " GyroAng: " + "{:.4f}".format(GyroAng) + " GyroSpeed" + "{:.4f}".format(sGyro_val))
    
    # if gyro_val > 20:
    #     DRIVE_SPEED = 60
    # elif gyro_val < -20:
    #     DRIVE_SPEED = 40

    ##################### Grab can in front of robot ###############################
    # if (sLightC_val >= 300) and not can_flag:
    #     ev3.Sound.beep().wait()
    #     mRight.duty_cycle_sp = 0
    #     mLeft.duty_cycle_sp = 0
    #     mClaw.run_to_rel_pos(position_sp=GRAB_ANGLE, speed_sp=200, stop_action="hold")
    #     sleep(1)   # Give the motor time to move
    #     #mClaw.run_to_rel_pos(position_sp=RELEASE_ANGLE, speed_sp=100, stop_action="coast")
    #     setMotorSP(mRight, -TURN_SPEED)
    #     setMotorSP(mLeft,   TURN_SPEED)
    #     sleep(1.2)
    #     sColorR_val= sColorR.value() #Load new sensor value
    #     while sColorR_val > 20:
    #         sColorR_val= sColorR.value() #Load new sensor value
    #         sleep(0.001)
    #     integral   = 0 #Reset PID
    #     last_error = 0 #Reset PID
    #     can_flag = True #Set flag that can has been grabbed
    #     ev3.Sound.beep().wait()

    # - - - LOG DATA - - -
    error_log   .append(error)
    integral_log.append(integral)
    sColorL_log .append(sColorL_val)
    sColorR_log .append(sColorR_val)
    sLightC_log .append(sLightC_val)
    sGyro_log   .append(sGyro_val)
    GyroAng_log .append(GyroAng)

    ##################### If button pressed, end program ###############################
    if btn.any(): ########
        mRight.duty_cycle_sp = 0
        mLeft.duty_cycle_sp = 0
        ev3.Sound.beep().wait()
        exit_cond = False

#- - - - - - - - - - END PROGRAM - - - - - - - - - -
if can_flag:
    mClaw.run_to_rel_pos(position_sp=RELEASE_ANGLE, speed_sp=100, stop_action="coast")

# - - - Write data logs to csv - - -
with open('test_data.csv', 'w') as f:
    for i in range(len(error_log)):
        f.write("{};{};{};{};{};{};{};{};\n".format(
            i, 
            error_log[i], 
            integral_log[i],
            sColorL_log[i], 
            sColorR_log[i], 
            sLightC_log[i],
            sGyro_log[i], 
            GyroAng_log[i]))
    #for element in sGyro_log:
    #    f.write("{};\n".format(element))
