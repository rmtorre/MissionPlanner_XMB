# -*- coding: utf-8 -*-
"""
Script de Partida do Dractor 25-A

A aeronave tenta dar partida 10 vezes, alterando a posição da borboleta do motor.
Uma vez que o sensor de rotação entende que foi dada a partida, o motor é colocado em marcha lenta.
Em seguida, o sensor de rotação confere se o motor está rodando. Se estiver tudo certo, a ventuinha será ligada e o modo de voo será alterado para Loiter.


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

print 'Iniciando a Partida do Dractor 25A...'
MissionPlanner.MainV2.speechEngine.SpeakAsync("Ligando")

#Definition of variables
# max_pwm_start_array = [0.4, 0.6, 0.8, 1, 0.4, 0.6, 0.8, 1, 0.8, 0.8]
max_pwm_start_array = [0.12 , 0.15, 0.20, 0.3, 0.35, 0.25, 0.3, 0.1, 0.2, 0.3]

starting_phase = 0
start_trials = 0
state_time = 0

relay = False
pwm_starter = 0
pwm_servo = 0
pwm_fan = 0
pwm_killswitch = 0

PUMP_CHANNEL=12
PUMP_MAX_PWM=1900
PUMP_MIN_PWM=1000
time_pump=0.75

voltage =cs.battery_voltage
rpm = 0
LOOP_PERIOD = 20

VOLTAGE_MIN = 47.0 #47.0
VOLTAGE_MAX = 50.6 #50.5

#PWMs Channels
PWM_STARTER_CHANNEL = 10 #
PWM_SERVO_CHANNEL = 13 
PWM_KILLSWITCH_CHANNEL = 15 
PWM_FAN_CHANNEL = 11 

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
#PWM_FAN_MAX=Script.GetParam('SERVO'+str(int(PWM_FAN_CHANNEL))+'_MAX')
PWM_FAN_MAX=1450
PWM_FAN_RANGE = PWM_FAN_MAX - PWM_FAN_MIN
PWM_FAN_OFFSET = PWM_FAN_MIN

#Definition os States
class STARTING_STATES():
    FAILED = -1
    STOPPED = 0
    ACTIVATE = 1
    RISE = 2
    FALL = 3
    DEACTIVATE = 4
    RPM_CHECK = 5
    SUCCESS = 6

class STARTER_STATES():
    FAILED = -1
    STOPPED = 0
    STARTING = 1
    SUCCESS = 2
    
current_starter_state = STARTER_STATES.STOPPED
current_starting_state = STARTING_STATES.STOPPED
       
def saturation(value, value_min, value_max):
    if value < value_min:
        return value_min
    if value > value_max:
        return value_max
    return value
    
def initialize():
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, (1-0) * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0)
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_STARTER_CHANNEL, 0 * PWM_STARTER_RANGE + PWM_STARTER_OFFSET, 0,0,0,0,0)
    # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_KILLSWITCH_CHANNEL, 0 * PWM_KILLSWITCH_RANGE + PWM_KILLSWITCH_OFFSET, 0,0,0,0,0)
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 2, 0, 0,0,0,0,0) # kill switch
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_FAN_CHANNEL, 0 * PWM_FAN_RANGE + PWM_FAN_OFFSET, 0,0,0,0,0)
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 1, 0, 0,0,0,0,0)
    print 'Falha na Partida do Motor. Execute o Script novamente.'

#Ramp of PWM in order to turn on the fan    
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
    
#State Machine for Starting Procedures
def starting_m(current_time):
    global relay, pwm_starter, state_time, current_starting_state, pwm_killswitch
    if current_starting_state == STARTING_STATES.FAILED:
        pwm_killswitch = 0
        relay = False
        if(current_time - state_time) >= 5950:
            current_starting_state = STARTING_STATES.STOPPED
    elif current_starting_state == STARTING_STATES.STOPPED:
        #print 'Activating Starter Relay'
        current_starting_state = STARTING_STATES.ACTIVATE
    elif current_starting_state == STARTING_STATES.ACTIVATE:
        pwm_killswitch = 1
        relay = True
        if (current_time - state_time) >= 300:
            #print 'Rising...'
            current_starting_state = STARTING_STATES.RISE
    elif current_starting_state == STARTING_STATES.RISE:
        pwm_killswitch = 1
        relay = True
        pwm_starter = saturation(0.9 * ((current_time - state_time)-300) / 1600, 0, 0.9)
        if (current_time - state_time) >= 1900:
            #print 'Falling...'
            current_starting_state = STARTING_STATES.FALL
    elif current_starting_state == STARTING_STATES.FALL:
        pwm_killswitch = 1
        relay = True
        pwm_starter = saturation(0.9 - ((current_time - state_time) - 1900) * 0.9 / 150,0,0.9)
        if (current_time - state_time) >= 2050:
            #print 'Deactivating Starter Relay'
            current_starting_state = STARTING_STATES.DEACTIVATE
    elif current_starting_state == STARTING_STATES.DEACTIVATE:
        pwm_killswitch = 1
        if (current_time - state_time) >= 2550:
            relay = False
            #print 'Checking for RPM'
            current_starting_state = STARTING_STATES.RPM_CHECK
    elif current_starting_state == STARTING_STATES.RPM_CHECK:
        pwm_killswitch = 1
        if (current_time - state_time) >= 6000: #3950 antigo
            if rpm > 1800:
                #print 'Done'
                current_starting_state = STARTING_STATES.SUCCESS
            else:
                #print 'try again...'
                current_starting_state = STARTING_STATES.FAILED
                

def calibrate(channel,pwm_max,pwm_min,time_in_seconds):
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, channel, pwm_max, 0,0,0,0,0)
    time.sleep(time_in_seconds)
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, channel, pwm_min, 0,0,0,0,0)


#State Machine for Start Procedures
def starter_m(current_time):
    global start_trials, state_time, pwm_servo, current_starting_state, current_starter_state 
    
    if current_starter_state == STARTER_STATES.FAILED:
        pwm_servo = 0
        # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, (1-pwm_servo) * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0)
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, pwm_servo * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0) # Invertido Agora
        current_starter_state = STARTER_STATES.FAILED
    elif current_starter_state == STARTER_STATES.STOPPED:
        print 'Dando a partida no gerador'
        print 'Tentativa numero: ', start_trials
        # print 'Servo PWM at: ', pwm_servo
        state_time = current_time
        current_starter_state = STARTER_STATES.STARTING
    elif current_starter_state == STARTER_STATES.STARTING:
        if start_trials < 10:
            pwm_servo = max_pwm_start_array[start_trials]
            starting_m(current_time)
        if current_starting_state == STARTING_STATES.STOPPED and start_trials < 10:
            start_trials += 1
            print 'Partida Interrompida'
            state_time = current_time
            current_starter_state = STARTER_STATES.STOPPED
        elif current_starting_state == STARTING_STATES.STOPPED and start_trials >= 10:
            start_trials += 1
            print 'Partida Falhou'
            state_time = current_time
            current_starter_state = STARTER_STATES.FAILED
        elif current_starting_state == STARTING_STATES.SUCCESS:
            print 'Partida com Sucesso :D'
            state_time = current_time
            current_starter_state = STARTER_STATES.SUCCESS
            pwm_servo = 0.18 # Marcha Lenta
            
    elif current_starter_state == STARTER_STATES.SUCCESS:

        current_starter_state = STARTER_STATES.SUCCESS
       

#Set all channels in Pix to Zero in order to avoid issues related to channel assignment
def set_zero_servo_channels(channel_list):
    for ch in channel_list:
        name='SERVO'+str(int(ch))+'_FUNCTION'
        value=0
        Script.ChangeParam(name,value)
    #print 'Servo Functions Setted to 0'

#Set Standard Servo Functions to Zero in order to ensure that it will be able to be activated 
ch_list = [PWM_STARTER_CHANNEL,PWM_FAN_CHANNEL,PWM_SERVO_CHANNEL,PWM_KILLSWITCH_CHANNEL]
# ch_list = [PWM_STARTER_CHANNEL,PWM_FAN_CHANNEL,PWM_KILLSWITCH_CHANNEL]
set_zero_servo_channels(ch_list)

#Initialize channels with 0
# MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, (1-0) * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0)
MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, PWM_SERVO_OFFSET, 0,0,0,0,0) # Invertido Agora 
MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_STARTER_CHANNEL, 0 * PWM_STARTER_RANGE + PWM_STARTER_OFFSET, 0,0,0,0,0)
# MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_KILLSWITCH_CHANNEL, 0 * PWM_KILLSWITCH_RANGE + PWM_KILLSWITCH_OFFSET, 0,0,0,0,0)
MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 2, 0, 0,0,0,0,0) # Kill Switch Relay

MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 1, 0, 0,0,0,0,0) # Relay de Partida
MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_FAN_CHANNEL, 0 * PWM_FAN_RANGE + PWM_FAN_OFFSET, 0,0,0,0,0)


# PUMP
calibrate(PUMP_CHANNEL,PUMP_MAX_PWM,PUMP_MIN_PWM,time_pump)
print('Bomba Calibrada')

#Check if the battery Voltage is within Voltage Specs
voltage =cs.battery_voltage
if(voltage < VOLTAGE_MIN):
    print 'Procedimento cancelado. Recarregue a Bateria, por favor.'
    current_starter_state = STARTER_STATES.FAILED
if(voltage > VOLTAGE_MAX):
    print 'Procedimento cancelado. Tensao da Bateria acima do especificado'
    current_starter_state = STARTER_STATES.FAILED

timeout = (time.time() * 1000)+1500

while (current_starter_state <> STARTER_STATES.SUCCESS) and (current_starter_state <> STARTER_STATES.FAILED):
    if (time.time() * 1000) >= timeout:
        
        rpm = cs.rpm1
        voltage =cs.battery_voltage
        time.sleep(1.75)
        rpm = cs.rpm1
        starter_m(time.time() * 1000)
        print rpm, ',', pwm_servo, ',', pwm_starter, ',', relay, ',', pwm_killswitch
        pwm_servo = saturation(pwm_servo, 0, 1)
        pwm_starter = saturation(pwm_starter,0,1)
        
        # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, (1-pwm_servo) * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0)
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, pwm_servo * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0) # Invertido Agora
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_STARTER_CHANNEL, pwm_starter * PWM_STARTER_RANGE + PWM_STARTER_OFFSET, 0,0,0,0,0)
        # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_KILLSWITCH_CHANNEL, pwm_killswitch * PWM_KILLSWITCH_RANGE + PWM_KILLSWITCH_OFFSET, 0,0,0,0,0)
        # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 2, 1 if relay else 0, 0,0,0,0,0) # kill  
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 2, pwm_killswitch, 0,0,0,0,0) # kill 
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 1, 1 if relay else 0, 0,0,0,0,0)
        timeout = timeout + LOOP_PERIOD
        
 
time.sleep(3)
rpm = cs.rpm1
 
if(rpm> 1800 and current_starter_state <> STARTER_STATES.FAILED):
    turnON_fan(8.0,0.2)
    # Read again RPM and decide
    time.sleep(2)
    rpm=cs.rpm1
    if(rpm> 1800 and current_starter_state <> STARTER_STATES.FAILED):
        Script.ChangeMode('LOITER') 
        print 'Modo Loiter Ativado'
        print 'Pronto para Armar e Voar!'
        MissionPlanner.MainV2.speechEngine.SpeakAsync("Pronto para voar! Tenha um bom voo")
    else:  # Desliga e manda começar de novo
        initialize()
else: # Desliga e manda começar de novo
    initialize()
    # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, (1-0) * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0)
    # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_STARTER_CHANNEL, 0 * PWM_STARTER_RANGE + PWM_STARTER_OFFSET, 0,0,0,0,0)
    # # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_KILLSWITCH_CHANNEL, 0 * PWM_KILLSWITCH_RANGE + PWM_KILLSWITCH_OFFSET, 0,0,0,0,0)
    # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 2, 0, 0,0,0,0,0) # kill switch
    # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_FAN_CHANNEL, 0 * PWM_FAN_RANGE + PWM_FAN_OFFSET, 0,0,0,0,0)
    # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, 1, 0, 0,0,0,0,0)
    # print 'Falha na Partida do Motor. Execute o Script novamente.'
