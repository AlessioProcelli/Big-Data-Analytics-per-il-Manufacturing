# Usa l'immagine ufficiale di Python come base
FROM python:3.9-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il tuo script nel container
COPY kafka_client.py /app/

# Installa le librerie necessarie
RUN pip install confluent_kafka

# Comando per eseguire il tuo producer
CMD ["python", "kafka_client.py"]
