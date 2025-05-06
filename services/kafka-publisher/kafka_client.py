from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='kafka:9092')

def delivery_callback(err, msg):
    if err is not None:
        print(f"Errore nel delivery del messaggio: {err}")
    else:
        print(f"Messaggio inviato a {msg.topic()} [{msg.partition()}]")

# Configura il producer per connettersi a Kafka
producer = Producer({'bootstrap.servers': 'kafka:9092'})  # 'kafka' è il nome del servizio nel Docker Compose

# Produce un messaggio di test
producer.produce('test-topic', key='key', value='Test messaggio', callback=delivery_callback)

# Aspetta che tutti i messaggi siano inviati
producer.flush()
