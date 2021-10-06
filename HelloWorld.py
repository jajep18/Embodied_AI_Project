import ev3dev.ev3 as ev3
from time import sleep
import signal

btn = ev3.Button()

mL = ev3.LargeMotor('outA')
mR = ev3.LargeMotor('outD')

BASE_SPEED = 30
TURN_SPEED = 80

#ev3.Sound.play('BattleMusic.wav')


# lightSensor = ev3.LightSensor('in1')
# touchSensor = ev3.TouchSensor('in4')

#assert lightSensor.connected, "Light sensor is not connected"
#assert touchSensor.connected, "Touch sensor is not connected"

mL.run_direct()
mR.run_direct()

while True:
    mL.duty_cycle_sp = BASE_SPEED
    mR.duty_cycle_sp = BASE_SPEED

    if btn.any():
        ev3.Sound.beep().wait()
        mL.duty_cycle_sp = 0
        mR.duty_cycle_sp = 0
        exit()