# -*- coding: utf-8 -*-
"""
Script de Limpeza da Bomba

A aeronave aciona a bomba por 1 minuto para limpar o dractor.

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

def clean_pump(channel,pwm_max,pwm_min,time_in_seconds):
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, channel, pwm_max, 0,0,0,0,0)
    time.sleep(time_in_seconds)
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, channel, pwm_min, 0,0,0,0,0)



print 'Iniciando a Limpeza do Sistema de Pulverização...'
MissionPlanner.MainV2.speechEngine.SpeakAsync("Limpando o Sistema de Pulverização")

PUMP_CHANNEL=12
PUMP_MAX_PWM=1900
PUMP_MIN_PWM=1000
time_pump=60*5

MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PUMP_CHANNEL, PUMP_MIN_PWM, 0,0,0,0,0)

time.sleep(1)

calibrate(PUMP_CHANNEL,PUMP_MAX_PWM,PUMP_MIN_PWM,3)
clean_pump(PUMP_CHANNEL,PUMP_MAX_PWM,PUMP_MIN_PWM,time_pump)
print 'Sistema Limpo'
MissionPlanner.MainV2.speechEngine.SpeakAsync("Sistema Limpo")

