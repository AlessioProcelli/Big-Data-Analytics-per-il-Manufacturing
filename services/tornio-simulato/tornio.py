import time
import random
import os  
from opcua import Server
import logging

class Tornio:
    def __init__(self):
        #Parametri dalle variabili d'ambiente
        self.url = os.getenv("MACHINE_URL", "opc.tcp://0.0.0.0:4840/")
        self.nameSpace = os.getenv("MACHINE_NAMESPACE", "Tornio_OPC-UA")
        self.latheName=os.getenv("LATHE_NAME","Tornio Indefinito")
        
        
        # Variabili per la simulazione del tornio
        self.spindle_speed = 0          # Velocità del mandrino (RPM)
        self.feed_rate = 0              # Avanzamento utensile (mm/s)
        self.tool_position = 0          # Posizione utensile (mm)
        self.temperature = 25           # Temperatura (°C)
        self.vibrations = 0             # Vibrazioni (m/s²)
        self.tool_wear = 0              # Usura utensile (%)
        self.running = False            # Stato del tornio
        self.tool_changes = 0           # Numero di cambi utensile
        
        self.CreateServerAndObject(self.url, self.nameSpace)
        
        logging.basicConfig(filename='../log/tornio.log', level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s  ")
        
                
        # Imposta le variabili scrivibili
        self.spindle_speed_var.set_writable()
        self.feed_rate_var.set_writable()
        
    def CreateServerAndObject(self, url, nameSpace):
        self.server = Server()
        self.server.set_endpoint(url)
        ns = self.server.register_namespace(nameSpace)
        self.lathe_obj = self.server.nodes.objects.add_object(ns, "Lathe")
        self.spindle_speed_var = self.lathe_obj.add_variable(ns, "SpindleSpeed", 0)
        self.feed_rate_var = self.lathe_obj.add_variable(ns, "FeedRate", 0.0)
        self.tool_position_var = self.lathe_obj.add_variable(ns, "ToolPosition", 0.0)
        self.temperature_var = self.lathe_obj.add_variable(ns, "Temperature", 25.0)
        self.vibrations_var = self.lathe_obj.add_variable(ns, "Vibrations", 0.0)
        self.tool_wear_var = self.lathe_obj.add_variable(ns, "ToolWear", 0.0)
        self.running_var = self.lathe_obj.add_variable(ns, "Running", False)
        self.tool_changes_var = self.lathe_obj.add_variable(ns, "ToolChanges", 0)
        
    def start(self, rpm, feed_rate):
        self.spindle_speed = rpm
        self.feed_rate = feed_rate
        self.running = True

    def stop(self):
        self.spindle_speed = 0
        self.feed_rate = 0
        self.running = False

    def update(self):
        if self.running:
            self.tool_position += self.feed_rate * 0.1  
            self.temperature += max(0.1, random.gauss(0.5, 0.25)) * (self.spindle_speed / 1000)  
            self.vibrations = max(0.1, random.gauss(0.55, 0.25)) * (self.spindle_speed / 500)
            self.tool_wear +=max(0.01, random.gauss(0.09, 0.08))
            
        if self.tool_wear >= 95:
            self.change_tool()

    def change_tool(self):
        self.tool_changes += 1
        self.tool_wear = 0  # Reset dell'usura utensile
        logging.info(f"{self.latheName} - Cambio utensile effettuato! Totale cambi: {self.tool_changes}")
        

    def get_status(self):
        return {
            "SpindleSpeed": self.spindle_speed,
            "FeedRate": self.feed_rate,
            "ToolPosition": round(self.tool_position, 2),
            "Temperature": round(self.temperature, 1),
            "Vibrations": round(self.vibrations, 2),
            "ToolWear": round(self.tool_wear, 1),
            "Running": self.running,
            "ToolChanges": self.tool_changes  
        }
    
    def run_server(self):
        spindleSpeed = int(os.getenv("SPINDLE_SPEED", 100))
        feedRate = float(os.getenv("FEED_RATE", 0.5)) 
        
        self.server.start()
        logging.info(f"{self.latheName} - Server OPC-UA avviato su {self.server.endpoint}")
        try:
            while True:
                self.start(spindleSpeed, feedRate)
                self.update()
                status = self.get_status()
                self.spindle_speed_var.set_value(status["SpindleSpeed"])
                self.feed_rate_var.set_value(status["FeedRate"])
                self.tool_position_var.set_value(status["ToolPosition"])
                self.temperature_var.set_value(status["Temperature"])
                self.vibrations_var.set_value(status["Vibrations"])
                self.tool_wear_var.set_value(status["ToolWear"])
                self.running_var.set_value(status["Running"])
                self.tool_changes_var.set_value(status["ToolChanges"]) 
                time.sleep(5)
                
        except KeyboardInterrupt:
            self.server.stop()
            logging.info(f"{self.latheName} - Server OPC-UA fermato.")

if __name__ == "__main__":
    tornio = Tornio()
    tornio.run_server()
