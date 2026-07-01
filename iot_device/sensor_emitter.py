import requests
import time
import random

API_URL = "http://localhost:8000/lecturas/"
TOKEN_URL = "http://localhost:8000/token"
ESTACION_ID = 1

def obtener_token_automatico():
    print("--- Solicitando token al servidor... ---")
    try:
        response = requests.post(TOKEN_URL)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("[OK] Token obtenido con éxito.")
            return token
        else:
            print(f"[ERROR] No se pudo obtener el token. Código: {response.status_code}")
            return None
    except Exception as e:
        print(f"[CRÍTICO] Error al conectar con el login: {e}")
        return None

def leer_sensor_emulado():
    return round(random.uniform(10.5, 85.0), 2)

def enviar_telemetria():
    token_jwt = obtener_token_automatico()
    
    if not token_jwt:
        print("Emisor detenido porque no hay token.")
        return

    print(f"--- Iniciando Emisor IoT para Estación {ESTACION_ID} ---")
    
    headers = {
        "Authorization": f"Bearer {token_jwt}"
    }
    
    while True:
        valor = leer_sensor_emulado()
        payload = {
            "valor": valor,
            "estacion_id": ESTACION_ID
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"[OK] Lectura enviada: {valor} cm")
            else:
                print(f"[ERROR] Código: {response.status_code}")
        except Exception as e:
            print(f"[CRÍTICO] No hay conexión con el servidor: {e}")
        
        if valor > 70.0:
            print("[ALERTA] Umbral de inundación superado.")
            time.sleep(2)
        else:
            time.sleep(10)

if __name__ == "__main__":
    enviar_telemetria()