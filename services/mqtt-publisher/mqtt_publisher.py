import paho.mqtt.client as mqtt
import random
import time

BROKER_ADDRESS = "mqtt-broker"  # Nome del servizio nel docker-compose
TOPIC = "sensors/temperature"

client = mqtt.Client()
client.connect(BROKER_ADDRESS, 1883, 60)

try:
    while True:
        temperature = round(random.uniform(0, 100), 2)  # Valore tra 20 e 30°C
        client.publish(TOPIC, temperature)
        print(f"Pubblicato: {temperature} su {TOPIC}")
        time.sleep(15)  # Invia ogni 2 secondi

except KeyboardInterrupt:
    print("Interrotto.")
finally:
    client.disconnect()