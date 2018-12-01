#!/usr/bin/python

import sys
from phue import Bridge
import numpy as np
import time

import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()

# approximation valid for
# 0 degC < T < 60 degC
# 1% < RH < 100%
# 0 degC < Td < 50 degC 
 
 
def dewpoint_approximation(T,RH):
    # constants
    _a = 17.271
    _b = 237.7 # degC
 
    Td = (_b * gamma(T,RH)) / (_a - gamma(T,RH))
 
    return Td
 
 
def gamma(T,RH):
    # constants
    _a = 17.271
    _b = 237.7 # degC
 
    g = (_a * T / (_b + T)) + np.log(RH/100.0)
 
    return g
 
 

while True:
    b = Bridge('localhost')
    
    sensors = b.get_sensor_objects('id')
    sensorDb = dict()

    for id in sensors.keys():
        # print(id)
        # print(sensors[id].uniqueid)
        sensorKey = sensors[id].uniqueid[:26]
        if not sensorKey in sensorDb:
            sensorDb[sensorKey] = []
        sensorDb[sensorKey].append(sensors[id])
    
    for s in sensorDb.keys():
        temperature = None
        humidity = None
        pressure = None
        dewpoint = None
        for ss in sensorDb[s]:
            # print(ss.uniqueid)
            # print(ss.name)
            if 'temperature' in ss.state:
                temperature = float(ss.state['temperature'])/100
                print("temperature {}".format(temperature))
            elif 'humidity' in ss.state:
                humidity = float(ss.state['humidity'])/100
                print("humidity {}".format(humidity))
            elif 'pressure' in ss.state:
                pressure = float(ss.state['pressure'])
                print("pressure {}".format(pressure))
        if  humidity is not None and temperature is not None: 
            dewpoint = dewpoint_approximation(temperature,humidity)
            
            print("dewpoint {}".format(dewpoint))
    
        if  humidity is not None or temperature is not None or pressure is not None:
            objectname = ss.uniqueid[:26].replace(":", "_")
            print(objectname)
            if  temperature is not None:
                client.publish(objectname +"/temperature", temperature)
            if  pressure is not None:
                client.publish(objectname +"/humidity", humidity)
            if  pressure is not None:
                client.publish(objectname +"/pressure", pressure)
            if  dewpoint is not None:
                client.publish(objectname +"/dewpoint", dewpoint)
        print(' ')
                
    time.sleep(15)
        
        
            

    