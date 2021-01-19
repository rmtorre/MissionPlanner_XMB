# -*- coding: utf-8 -*-
"""
Script para inicializar os valores nos canais de PWM auxiliares

Relay de Partida e da Ignição desligam
Bomba desliga
Ventoinha desliga
Si]nal do gerador (partida) vai para o minimo

@author: Xmobots
"""

import time
import clr
import MissionPlanner

clr.AddReference("MissionPlanner")
clr.AddReference("MissionPlanner.Utilities")
clr.AddReference("MAVLink")
import MAVLink

# Check if vehicle is armed

armed=cs.armed

if armed:
    print 'Veiculo armado, não é possivel rodar o script'
else:
    print 'Veiculo Disarmado, voltando servos as posições iniciais.'

## Inputs
PUMP_CHANNEL=12
PUMP_MAX_PWM=1900
PUMP_MIN_PWM=1000


#PWMs Channels
PWM_STARTER_CHANNEL = 10 #11
PWM_SERVO_CHANNEL = 13 #9
PWM_KILLSWITCH_CHANNEL = 15 #12
PWM_FAN_CHANNEL = 11 #10

#PWMs MAX/MIN/Offsets/Ranges
PWM_STARTER_MIN = Script.GetParam('SERVO'+str(int(PWM_STARTER_CHANNEL))+'_MIN')
PWM_STARTER_MAX = Script.GetParam('SERVO'+str(int(PWM_STARTER_CHANNEL))+'_MAX')
PWM_STARTER_RANGE = PWM_STARTER_MAX - PWM_STARTER_MIN
PWM_STARTER_OFFSET = PWM_STARTER_MIN


PWM_SERVO_MIN = Script.GetParam('SERVO'+str(int(PWM_SERVO_CHANNEL))+'_MIN')
PWM_SERVO_MAX = Script.GetParam('SERVO'+str(int(PWM_SERVO_CHANNEL))+'_MAX')
PWM_SERVO_RANGE = PWM_SERVO_MAX - PWM_SERVO_MIN
# PWM_SERVO_OFFSET = PWM_SERVO_MIN
PWM_SERVO_OFFSET = PWM_SERVO_MIN # invertido agora 

# print PWM_SERVO_MIN, PWM_SERVO_MAX, PWM_SERVO_RANGE, PWM_SERVO_OFFSET

PWM_KILLSWITCH_MIN=Script.GetParam('SERVO'+str(int(PWM_KILLSWITCH_CHANNEL))+'_MIN')
PWM_KILLSWITCH_MAX=Script.GetParam('SERVO'+str(int(PWM_KILLSWITCH_CHANNEL))+'_MAX')
PWM_KILLSWITCH_RANGE = PWM_KILLSWITCH_MAX - PWM_KILLSWITCH_MIN
PWM_KILLSWITCH_OFFSET = PWM_KILLSWITCH_MIN

PWM_FAN_MIN=Script.GetParam('SERVO'+str(int(PWM_FAN_CHANNEL))+'_MIN')
PWM_FAN_MAX=1450
PWM_FAN_RANGE = PWM_FAN_MAX - PWM_FAN_MIN
PWM_FAN_OFFSET = PWM_FAN_MIN

#Initialize channels with 0
if not armed:
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, PWM_SERVO_OFFSET, 0,0,0,0,0) # Invertido Agora 
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_STARTER_CHANNEL, 0 * PWM_STARTER_RANGE + PWM_STARTER_OFFSET, 0,0,0,0,0)
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 2, 0, 0,0,0,0,0) # Kill Switch Relay
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 1, 0, 0,0,0,0,0) # Relay de Partida
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_FAN_CHANNEL, 0 * PWM_FAN_RANGE + PWM_FAN_OFFSET, 0,0,0,0,0) # Ventuinha
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PUMP_CHANNEL, PUMP_MIN_PWM, 0,0,0,0,0) # PUMP


