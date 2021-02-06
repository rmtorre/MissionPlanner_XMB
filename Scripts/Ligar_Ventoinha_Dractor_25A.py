# -*- coding: utf-8 -*-
"""
Script de Limpeza da Bomba

O Script aciona a bomba por 4 segundos para testar.

Obs.: Não altere os valores abaixo.
Em caso de problemas, contate a XMOBOTS.


@author: Xmobots
"""

import time
import clr
import MissionPlanner

clr.AddReference("MissionPlanner")
clr.AddReference("MissionPlanner.Utilities")
clr.AddReference("MAVLink")
import MAVLink

def turnON_fan(ramp_time, increment_time):
    print 'Ligando Ventoinha!'
    for i in range(int(ramp_time/increment_time)):
        pwm_fan = (float(i+1))/(float(ramp_time/increment_time))
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_FAN_CHANNEL, pwm_fan * PWM_FAN_RANGE + PWM_FAN_OFFSET, 0,0,0,0,0)
        time.sleep(increment_time)
        print 'fan:', pwm_fan
    pwm_fan = 1.0    
    # print 'fan:', pwm_fan
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_FAN_CHANNEL, pwm_fan * PWM_FAN_RANGE + PWM_FAN_OFFSET, 0,0,0,0,0)
    print 'Ventoinha Ligada!'


print 'Ligando a ventoinha do Dractor...'
MissionPlanner.MainV2.speechEngine.SpeakAsync("Ligando a Ventoinha do Dractor 25A")

PWM_FAN_CHANNEL=11
PWM_FAN_MAX=1450
PWM_FAN_MIN=1000
PWM_FAN_RANGE = PWM_FAN_MAX - PWM_FAN_MIN
PWM_FAN_OFFSET = PWM_FAN_MIN

# First is needed to initialize PWM
MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_FAN_CHANNEL,PWM_FAN_MIN, 0,0,0,0,0)

time.sleep(1)
# Turn on FAN
turnON_fan(8.0,0.2)

print 'Pronto!'
MissionPlanner.MainV2.speechEngine.SpeakAsync("Pronto")

