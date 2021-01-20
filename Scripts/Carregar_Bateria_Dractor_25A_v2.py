# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 16:06:26 2021

Script para carregar 

@author: Rodrigo Torres
"""

import time
# import numpy as np
import clr
import MissionPlanner

clr.AddReference("MissionPlanner")
clr.AddReference("MissionPlanner.Utilities")
clr.AddReference("MAVLink")
import MAVLink


global n_samples
n_samples=25

class Voltage():
    def __init__(self):
        print ('Initializing')
        self.initial_time=time.time()
        self.voltage_list=[]
        self.voltage_list=[49]
        # self.voltage_list=[]
        self.delta_time_list=[np.nan]
        self.time_list=[time.time()]
    
    def update_voltage(self,voltage):
        
        self.voltage_list.append(voltage)
        
        self.delta_time_list.append(time.time()-self.time_list[-1])
        self.time_list.append(time.time())
        if len(self.voltage_list)>n_samples-1: # Take last 10 values
            self.voltage_list=self.voltage_list[-n_samples:]
            self.delta_time_list=self.delta_time_list[-n_samples:]
            
        print(self.voltage_list)
        
    def voltage_state(self):
        if len(self.voltage_list)<n_samples:
            self.Voltage_State='Unknown'
            self.current_voltage=self.voltage_list[-1]
            self.old_voltade=self.voltage_list[0]
            
        else:
            v1=(self.voltage_list[0]+self.voltage_list[1]+self.voltage_list[2])/3
            v2=(self.voltage_list[-1]+self.voltage_list[-2]+self.voltage_list[-3])/3
            self.current_voltage=v2
            self.old_voltade=v1
            if v2>v1:
                self.Voltage_State='Charging'
            else:
                self.Voltage_State='NotCharging'
    
    
class PID():
    
    def __init__(self):
        # self.target_voltage=48.0
        self.PID_Pgain=0.24
        self.PID_Dgain=0.012
        self.PID_Igain=0.012
        self.PID_Windupgain=5
        self.pwm_servo=0.15
        self.min_pwm_servo=0.15
        self.max_pwm_servo=0.30
        self.last_error=0
        self.last_integral=0
        self.last_command=self.pwm_servo
    
    def define_target_voltage(self,target_voltage):
        self.target_voltage=target_voltage
        print('Target Voltage defined at:',self.target_voltage)
        
    def calculate_pwm(self,voltage_state,voltage,sample_time):
        if voltage_state=='Unknown':
            self.pwm_servo=self.pwm_servo
        else:
            error=(self.target_voltage-voltage)
            P_gain=self.PID_Pgain*error
            if sample_time<=0.001:
                D_gain=0
                I_gain=0
            else:
                integral=self.last_integral+((self.last_command-self.pwm_servo)*self.PID_Windupgain*sample_time+error*self.PID_Igain)*sample_time
                I_gain=integral
                D_gain=self.PID_Dgain*(self.last_error-error)/sample_time
                # Update Values
                self.last_error=error
                self.last_integral=integral 
            self.pwm_servo=self.pwm_servo+P_gain+D_gain+I_gain
   
        
        # Saturate Commandas    
        self.pwm_servo=max(min(self.max_pwm_servo,self.pwm_servo),self.min_pwm_servo)
        self.last_command=self.pwm_servo
        print(self.pwm_servo)
        

## Params
# initial_voltage=45 #cs.voltage
initial_voltage=cs.battery_voltage
target_voltage=initial_voltage+1
# initial_value=0.15
# armed_state=False
armed_state=cs.armed
# rpm=10000#cs.rpm1
rpm=cs.rpm1
max_time=10 # In Seconds

PWM_SERVO_MIN =1100# Script.GetParam('SERVO'+str(int(PWM_SERVO_CHANNEL))+'_MIN')
PWM_SERVO_MAX =1900# Script.GetParam('SERVO'+str(int(PWM_SERVO_CHANNEL))+'_MAX')
PWM_SERVO_RANGE = PWM_SERVO_MAX - PWM_SERVO_MIN
PWM_SERVO_OFFSET = PWM_SERVO_MIN 

initial_time=time.time()

# voltage_list=[45]#[cs.voltage]

if armed_state == True:
    print('Não Execute o Script com a Aeronave Armada')
     

elif rpm<1800:
    print('Moto-Gerador não ligado. Execute o script de partida antes de carregar a bateria')

elif armed_state == False and rpm > 1800: # Aeronave no chao com motor ligado
    MissionPlanner.MainV2.speechEngine.SpeakAsync("Carregando a Bateria do Dractor 25 A")
    # Main Loop
    V=Voltage()
    V.voltage_state()
    PID=PID()
    PID.define_target_voltage(cs.voltage+1)
    
    while (time.time()-initial_time<max_time):# & (V.current_voltage<PID.target_voltage):
        # V.update_voltage(48+1*np.random.uniform(-1,1,1)[0])
        V.update_voltage(cs.battery_voltage)
        V.voltage_state()
        PID.calculate_pwm(V.voltage_state, V.current_voltage,V.delta_time_list[-1])
        
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, pwm_servo * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0) # Invertido Agora
        time.sleep(0.1)
        
        
    # Out of the Main Loop
    pwm_servo=0.15 # Marcha Lenta de Volta
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, PWM_SERVO_CHANNEL, pwm_servo * PWM_SERVO_RANGE + PWM_SERVO_OFFSET, 0,0,0,0,0) # Invertido Agora