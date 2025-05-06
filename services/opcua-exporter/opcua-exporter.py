import time
import logging
import os  
from opcua import Client
from prometheus_client import start_http_server, Gauge

class TornioExporter:
    def __init__(self):
        self.machine_server_url = os.getenv("MACHINE_SERVER_URL", "opc.tcp://tornio-opcua:4840/")
        self.max_retries = int(os.getenv("MAX_RETRIES", 2))
        self.retry_delay = int(os.getenv("RETRY_DELAY", 5))
        self.export_port = int(os.getenv("EXPORT_PORT", 9102))
        self.machineName = os.getenv("MACHINE_NAME", "Tornio")
        logging.basicConfig(filename="../log/opcua-exporter.log", level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        
        self.opcua_client = Client(self.machine_server_url)
        self.metrics = {
            "SpindleSpeed": Gauge(f'{self.machineName}_opcua_spindle_speed', 'Velocità mandrino (RPM)'),
            "FeedRate": Gauge(f'{self.machineName}_opcua_feed_rate', 'Avanzamento utensile (mm/s)'),
            "ToolPosition": Gauge(f'{self.machineName}_opcua_tool_position', 'Posizione utensile (mm)'),
            "Temperature": Gauge(f'{self.machineName}_opcua_temperature', 'Temperatura tornio (°C)'),
            "Vibrations": Gauge(f'{self.machineName}_opcua_vibrations', 'Vibrazioni (m/s²)'),
            "ToolWear": Gauge(f'{self.machineName}_opcua_tool_wear', 'Usura utensile (%)'),
            "Running": Gauge(f'{self.machineName}_running', 'Stato del tornio (1=ON, 0=OFF)'),
            "ToolChanges": Gauge(f'{self.machineName}_tool_changes', 'Numero di cambi utensile')
        }
        
        self.node_ids = {
            "SpindleSpeed": "ns=2;i=2",
            "FeedRate": "ns=2;i=3",
            "ToolPosition": "ns=2;i=4",
            "Temperature": "ns=2;i=5",
            "Vibrations": "ns=2;i=6",
            "ToolWear": "ns=2;i=7",
            "Running": "ns=2;i=8",
            "ToolChanges": "ns=2;i=9"
        }
    
    def connect(self):
        for attempt in range(self.max_retries):
            try:
                logging.info(f"Tentativo {attempt + 1} di connessione a {self.machine_server_url}...")
                self.opcua_client.connect()
                logging.info("Connesso al server OPC-UA")
                break
            except Exception as e:
                logging.error(f"Errore di connessione: {e}")
                if attempt < self.max_retries - 1:
                    logging.info(f"Riprovo tra {self.retry_delay} secondi...")
                    time.sleep(self.retry_delay)
                else:
                    logging.critical("Impossibile connettersi al server OPC-UA.")
                    exit(1)
    
    def fetch_data(self):
        while True:
            try:
                for key, node_id in self.node_ids.items():
                    node = self.opcua_client.get_node(node_id)
                    value = node.get_value()
                    self.metrics[key].set(value)
            except Exception as e:
                logging.warning(f"⚠️ Errore nel recupero dati OPC-UA: {e}")
            
            time.sleep(5)  

    def start_prometheus_server(self):
        start_http_server(self.export_port)
        logging.info(f" Exporter Prometheus in esecuzione su http://localhost:{self.export_port}")

    def run(self):
        self.connect() 
        self.start_prometheus_server() 
        self.fetch_data() 


if __name__ == "__main__":
    exporter = TornioExporter()
    exporter.run()
