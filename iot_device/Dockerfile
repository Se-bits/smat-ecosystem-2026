# Imagen base ligera de Python
FROM python:3.11-slim

# Definir el directorio de trabajo
WORKDIR /app

# Instalar las librerías directamente ya que son pocas
RUN pip install --no-cache-dir paho-mqtt requests

# Copiar el script del puente
COPY mqtt_bridge.py .

# Ejecutar el daemon
CMD ["python", "mqtt_bridge.py"]