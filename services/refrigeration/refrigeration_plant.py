import time
import random
import json
import os
import paho.mqtt.client as mqtt
from threading import Thread
import logging

# Parametri presi dalle variabili d'ambiente
BROKER = os.getenv("BROKER", "mqtt-broker") 
PORT = int(os.getenv("PORT", 1883))  
TOPIC = os.getenv("TOPIC", "impianto_refrigerazione/monitoraggio") 
TEMPERATURE_TARGET = float(os.getenv("TEMPERATURE_TARGET", 25)) 
DAY_TEMP_RANGE = tuple(map(int, os.getenv("DAY_TEMP_RANGE", "20,30").strip('"').split(',')))
NIGHT_TEMP_RANGE = tuple(map(int, os.getenv("NIGHT_TEMP_RANGE", "15,25").strip('"').split(',')))
ENERGY_COOLING = float(os.getenv("ENERGY_COOLING", 22.0)) 
ENERGY_HEATING = float(os.getenv("ENERGY_HEATING", 18.0))
MAX_FLOW = float(os.getenv("MAX_FLOW", 20.0))  
SIMULATION_INTERVAL = int(os.getenv("SIMULATION_INTERVAL", 1)) 

class RefrigerationPlant:
    def __init__(self):
        self.client = mqtt.Client()
        self.running = False
        self.thread = None
        self.current_temp = random.uniform(20.0, 30.0) 
        self.external_temp = self.simulate_external_temp() 
        logging.basicConfig(filename='../log/refrigeration.log', level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s  ")
    def get_time_of_day(self):
        current_hour = time.localtime().tm_hour
        if 6 <= current_hour < 18:
            return "day"
        else:
            return "night"

    def simulate_external_temp(self):
        time_of_day = self.get_time_of_day()
        if time_of_day == "day":
            return round(random.uniform(DAY_TEMP_RANGE[0], 
                                        DAY_TEMP_RANGE[1]), 2)
        else:
            return round(random.uniform(NIGHT_TEMP_RANGE[0],
                                        NIGHT_TEMP_RANGE[1]), 2)

    def calculate_flow(self, temperature):
        if temperature > TEMPERATURE_TARGET:
            flow = (temperature - TEMPERATURE_TARGET) * 0.5 
            flow_direction = "cooling"
        elif temperature < TEMPERATURE_TARGET:
            flow = (TEMPERATURE_TARGET - temperature) * 0.5 
            flow_direction = "heating"
        else:
            flow = 0
            flow_direction = "none"
        
        flow = min(flow, MAX_FLOW)  
        return round(flow, 2), flow_direction

    def calculate_energy_consumption(self, flow, flow_direction):
        if flow == 0:
            return 0
        if flow_direction == "cooling":
            return round(flow * ENERGY_COOLING, 2)
        elif flow_direction == "heating":
            return round(flow * ENERGY_HEATING, 2)
        return 0

    def adjust_temperature(self, temperature, flow, flow_direction, external_temp):
        if flow_direction == "cooling":
            temperature -= flow * 0.5
        elif flow_direction == "heating":
            temperature += flow * 0.5
        
        temperature += (external_temp - temperature) * 0.1
        return round(temperature, 2)

    def send_mqtt_data(self, temperature, flow, flow_direction, energy_consumption):
        payload = {
            "temperature": temperature,
            "flow": flow,
            "flow_direction": flow_direction,
            "energy_consumption": energy_consumption,
            "external_temp": self.external_temp
        }
        self.client.publish(TOPIC, json.dumps(payload))
        logging.info(f"Sent data: {json.dumps(payload, indent=2)}")

    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Connected to MQTT broker with result code {rc}")

    def start_simulation(self):
        self.running = True
        while self.running:
            self.external_temp = self.simulate_external_temp()
            flow, flow_direction = self.calculate_flow(self.current_temp)
            energy_consumption = self.calculate_energy_consumption(flow, flow_direction)
            self.current_temp = self.adjust_temperature(self.current_temp,
                                                        flow, flow_direction, 
                                                        self.external_temp)
            self.send_mqtt_data(self.current_temp, flow, flow_direction, energy_consumption)
            time.sleep(SIMULATION_INTERVAL)

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.connect(BROKER, PORT, 60)
        self.thread = Thread(target=self.start_simulation)
        self.thread.start()
        self.client.loop_start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.client.loop_stop()
        logging.info("Simulation stopped and MQTT connection closed.")

if __name__ == "__main__":
    plant = RefrigerationPlant()
    plant.start()
