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

def calibrate(channel,pwm_max,pwm_min,time_in_seconds):
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, channel, pwm_max, 0,0,0,0,0)
    time.sleep(time_in_seconds)
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, channel, pwm_min, 0,0,0,0,0)


print 'Calibrando a Bomba do Dractor...'
MissionPlanner.MainV2.speechEngine.SpeakAsync("Calibrando a Bomba do Dractor")

PUMP_CHANNEL=12
PUMP_MAX_PWM=1900
PUMP_MIN_PWM=1000


MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PUMP_CHANNEL, PUMP_MIN_PWM, 0,0,0,0,0)

time.sleep(0.75)

calibrate(PUMP_CHANNEL,PUMP_MAX_PWM,PUMP_MIN_PWM,3)

print 'Pronto!'
MissionPlanner.MainV2.speechEngine.SpeakAsync("Pronto")

