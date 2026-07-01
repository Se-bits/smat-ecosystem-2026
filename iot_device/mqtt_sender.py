import paho.mqtt.client as mqtt
import json
import time
import random

BROKER = "broker.hivemq.com" 
PORT = 1883
TOPIC = "fisi/smat/estaciones/1"

client = mqtt.Client()
client.connect(BROKER, PORT)

print("📡 Sensor Emulado MQTT transmitiendo ráfagas de datos...")


valor_estatico = 35.0 

while True:
    payload = {
       
        "valor": valor_estatico, 
        "timestamp": time.time()
    }
    
    client.publish(TOPIC, json.dumps(payload))
    print(f"Enviado por MQTT: {payload}")
    
    time.sleep(2)