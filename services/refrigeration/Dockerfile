# Usa un'immagine di Python
FROM python:3.10-slim

# Impostiamo una directory di lavoro
WORKDIR /app

# Copiamo i file necessari nel container
COPY . /app

# Installiamo le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Avvia il programma Python
CMD ["python", "refrigeration_plant.py"]
