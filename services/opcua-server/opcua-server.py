from opcua import Server
import random
import time

# Crea un'istanza del server OPC-UA
server = Server()

# Imposta l'endpoint del server (indica dove il server sarà accessibile)
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

# Imposta il server namespace
uri = "http://example.org"
idx = server.register_namespace(uri)

# Crea un oggetto personalizzato (un oggetto che rappresenta una parte del sistema)
objects = server.nodes.objects
myobj = objects.add_object(idx, "MyObject")

# Aggiungi una variabile all'oggetto (variabile della temperatura)
mytemp = myobj.add_variable(idx, "Temperature", 0)

# Imposta la variabile come sola lettura (non scrivibile)


# Avvia il server
server.start()
print("Server avviato. L'endpoint è:", server.endpoint)

try:
    while True:
        # Genera una temperatura casuale tra 0 e 100
        temperature_value = random.uniform(0, 100)
        mytemp.set_value(temperature_value)  # Imposta il valore della temperatura
        time.sleep(20)  # Rimuove il valore ogni secondo
        print(temperature_value)
except KeyboardInterrupt:
    print("Interruzione del server.")
finally:
    # Ferma il server al termine
    server.stop()
    print("Server fermato.")
