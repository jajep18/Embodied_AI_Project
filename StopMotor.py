#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from time import sleep
import signal

mA = ev3.LargeMotor('outA')
#mB = ev3.LargeMotor('outB')
mC = ev3.LargeMotor('outC')
mD = ev3.LargeMotor('outD')

mA.run_direct()
#mB.run_direct()
mC.run_direct()
mD.run_direct()

mA.duty_cycle_sp = 0
#mB.duty_cycle_sp = 0
mC.duty_cycle_sp = 0
mD.duty_cycle_sp = 0

exit()