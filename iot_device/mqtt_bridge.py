import paho.mqtt.client as mqtt
import requests
import json
import time
import threading
import os

# --- 1. CONFIGURACIÓN ---
BROKER = "broker.hivemq.com"
TOPIC = "fisi/smat/estaciones/#" 
API_URL = os.environ.get("API_URL", "http://localhost:8000/lecturas/")

LOGIN_URL = "http://localhost:8000/token" 
API_USER = "tu_usuario_backend" 
API_PASS = "tu_contraseña_backend"


print("Autenticando con el backend para obtener el JWT...")
login_response = requests.post(LOGIN_URL, data={"username": API_USER, "password": API_PASS})

if login_response.status_code == 200:
    TOKEN = login_response.json().get("access_token")
    print("✅ Token capturado exitosamente por el script.")
else:
    print(f"❌ Error al obtener el token: {login_response.text}")
    exit() 


cache_filtro = {}

last_seen = {}

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        
        estacion_id = msg.topic.split("/")[-1]
        
        last_seen[estacion_id] = time.time()
        
        nuevo_valor = float(payload["valor"])
        tiempo_actual = time.time()
        
        print(f"\n📡 Telemetría recibida -> Estación [{estacion_id}]: {nuevo_valor} cm")

        debe_enviar = False
        razon = ""

        if estacion_id not in cache_filtro:
            debe_enviar = True
            razon = "Primer registro de la estación en esta sesión."
        else:
            datos_previos = cache_filtro[estacion_id]
            ultimo_valor = datos_previos["valor"]
            ultimo_tiempo = datos_previos["timestamp"]

            if ultimo_valor != 0:
                variacion = abs(nuevo_valor - ultimo_valor) / ultimo_valor
            else:
                variacion = abs(nuevo_valor - ultimo_valor)

            if variacion > 0.05:
                debe_enviar = True
                razon = f"Variación mayor al 5% (Cambió un {variacion * 100:.2f}%)"
            elif (tiempo_actual - ultimo_tiempo) > 60:
                debe_enviar = True
                razon = f"Reporte mínimo de vida (>60 segundos sin transmitir)"

        if debe_enviar:
            print(f"✅ [Filtro Aceptado] -> Razón: {razon}")
            
            data_to_send = {
                "valor": nuevo_valor,
                "estacion_id": int(estacion_id)
            }
            
            headers = {"Authorization": f"Bearer {TOKEN}"}
            response = requests.post(API_URL, json=data_to_send, headers=headers)
            
            if response.status_code in [200, 201]:
                print(f"💾 [DB Sincronizada] Estación {estacion_id}: guardado {nuevo_valor} cm.")
                cache_filtro[estacion_id] = {
                    "valor": nuevo_valor,
                    "timestamp": tiempo_actual
                }
            else:
                print(f"❌ Error API ({response.status_code}): {response.text}")
        else:
            tiempo_restante = 60 - (tiempo_actual - cache_filtro[estacion_id]["timestamp"])
            print(f"🛑 [Filtro Bloqueado] -> Dato redundante. Próximo envío forzado en {int(tiempo_restante)}s")
            
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

def check_deadlines():
    while True:
        current_time = time.time()
        for eid, t in list(last_seen.items()):
            if current_time - t > 30: 
                print(f"🚨 ALERTA: Estación {eid} está OFFLINE")
        time.sleep(10)

threading.Thread(target=check_deadlines, daemon=True).start()

client = mqtt.Client()
client.on_message = on_message
print("📡 Bridge SMAT con Filtro de Ruido escuchando en el Broker...")
client.connect(BROKER, 1883)
client.subscribe(TOPIC)
client.loop_forever()